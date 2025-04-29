import asyncio
import collections

import asyncpg
from escpos.printer import Network
from loguru import logger
from tortoise import BaseDBAsyncClient, connections

from backend.database.models import Order
from backend.utils.order_text_manager import OrderTextManager

RETRY_DELAY = 5


async def get_order(order_id: int, connection: BaseDBAsyncClient):
    order = (
        await Order.filter(id=order_id)
        .prefetch_related(
            "order_menus__order_menu_fields__order_menu_field_products",
            "order_menus__order_menu_fields__order_menu_field_products__order_product_ingredients",
            "order_menus__menu__menu_fields",
            "order_menus__menu__menu_fields__field_products",
            "order_menus__menu__menu_fields__field_products__product__ingredients",
            "order_menus__menu__menu_fields__field_products__product__variants",
            "order_products__order_product_ingredients",
            "order_products__product__ingredients",
            "order_products__product__variants",
            "user__role__printers__printer",
        )
        .using_db(connection)
        .first()
    )

    return order


class PrintManager:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

        self.queues = collections.defaultdict(asyncio.Queue)
        self.printers: dict[int, Network] = {}
        self.order_futures: dict[int, asyncio.Future] = {}
        self.order_counters: dict[int, int] = collections.Counter()
        self.order_locks: dict[int, asyncio.Lock] = collections.defaultdict(
            asyncio.Lock
        )
        self.update_queue = asyncio.Queue()

        asyncio.create_task(self.update_worker())

    @classmethod
    async def create(cls):
        credentials = connections.db_config.get("default")["credentials"]
        pool = await asyncpg.create_pool(
            host=credentials["host"],
            port=credentials["port"],
            user=credentials["user"],
            database=credentials["database"],
            password=credentials["password"],
        )
        return cls(pool)

    def add_printer(self, printer_id: int, printer_ip_address: str):
        if printer_id not in self.printers:
            self.printers[printer_id] = Network(printer_ip_address, timeout=5)
            asyncio.create_task(self._worker(printer_id))

    async def _worker(self, printer_id: int):
        queue = self.queues[printer_id]
        printer = self.printers[printer_id]

        while True:
            job = await queue.get()
            content = job["content"]
            order_id = job["order_id"]

            while True:
                try:
                    await asyncio.to_thread(
                        self._print_content, printer, content
                    )
                except Exception as e:
                    logger.error(f"Print error on {printer.host}")
                    logger.exception(e)
                    await asyncio.sleep(RETRY_DELAY)

                    continue

                logger.success(f"Successfully printed on {printer.host}")
                break

            queue.task_done()

            async with self.order_locks[order_id]:
                self.order_counters[order_id] -= 1
                if self.order_counters[order_id] == 0:
                    future = self.order_futures.pop(order_id, None)
                    if future and not future.done():
                        future.set_result(True)

                    self.order_counters.pop(order_id, None)
                    self.order_locks.pop(order_id, None)

    @staticmethod
    def _print_content(printer: Network, content: str):
        if not printer.device:
            printer.open()

        for x in content.split("\n"):
            printer.set(align="left", font="a")
            printer.text(x if x else "\n")
        printer.cut()

    async def add_job(self, order_id: int, connection: BaseDBAsyncClient):
        order = await get_order(order_id, connection)

        if not order:
            return

        text = OrderTextManager(order)
        printers = order.user.role.printers

        async with self.order_locks[order_id]:
            self.order_counters[order_id] = len(printers)
            self.order_futures[order_id] = asyncio.Future()

        for role_printer in printers:
            p = role_printer.printer
            self.add_printer(p.id, p.ip_address)

            content = await text.generate_text_for_printer(
                role_printer.printer_type
            )
            await self.queues[p.id].put(
                {"content": content, "order_id": order_id}
            )

        asyncio.create_task(self.process_order_completion(order_id))

    async def process_order_completion(self, order_id: int):
        future = self.order_futures.get(order_id)
        if not future:
            return

        await future
        await self.update_queue.put(order_id)

    async def update_worker(self):
        while True:
            order_id = await self.update_queue.get()

            async with self.pool.acquire() as connection:
                async with connection.transaction():
                    await connection.execute(
                        'UPDATE "order" SET is_printed = true WHERE id = $1;',
                        order_id,
                    )

            self.update_queue.task_done()

            logger.success(f"Order {order_id} marked as printed.")
