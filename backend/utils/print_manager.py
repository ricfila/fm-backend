import asyncio
import collections
import re

import asyncpg
from escpos.printer import Network
from loguru import logger
from tortoise import BaseDBAsyncClient, connections

from backend.database.models import Order
from backend.utils import PrinterType
from backend.utils.order_text_manager import OrderTextManager

RETRY_DELAY = 5


async def get_order(order_id: int, connection: BaseDBAsyncClient):
    order = (
        await Order.filter(id=order_id)
        .prefetch_related(
            "order_menus__order_menu_fields__order_menu_field_products__order_product_ingredients__product_ingredient",
            "order_menus__menu",
            "order_products__order_product_ingredients__product_ingredient",
            "order_products__variant",
            "user__role__printers__printer",
            "confirmed_by__role__printers__printer",
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
        self.order_futures: dict[int, dict[str, asyncio.Future | bool]] = {}
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
                    future_data = self.order_futures.pop(order_id, None)
                    if future_data and not future_data["future"].done():
                        future_data["future"].set_result(True)

                    self.order_counters.pop(order_id, None)
                    self.order_locks.pop(order_id, None)

    @staticmethod
    def _print_content(printer: Network, content: str):
        printer.open()
        for line in re.split(r"(?<=\n)", content):
            printer.set(align="left", font="a")
            printer.text(line)
        printer.cut()

    async def add_job(
        self,
        order_id: int,
        connection: BaseDBAsyncClient,
        is_confirmed: bool = False,
        printer_types: list[PrinterType] | None = None,
    ):
        order = await get_order(order_id, connection)

        if not order:
            return

        text = OrderTextManager(order)

        printers = list(order.user.role.printers)
        printers_confirmed = (
            list(order.confirmed_by.role.printers)
            if order.confirmed_by
            else []
        )

        if is_confirmed:
            printers = printers_confirmed

        if printer_types:
            printers = [
                p
                for p in (printers + printers_confirmed)
                if p.printer_type in printer_types
            ]

        async with self.order_locks[order_id]:
            self.order_counters[order_id] = len(printers)
            self.order_futures[order_id] = {
                "future": asyncio.Future(),
                "is_confirmed": is_confirmed,
            }

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
        data = self.order_futures.get(order_id)
        if not data:
            return

        await data["future"]
        await self.update_queue.put((order_id, data["is_confirmed"]))

    async def update_worker(self):
        while True:
            order_id, is_confirmed = await self.update_queue.get()

            field_to_update = (
                "is_confirm_printed" if is_confirmed else "is_printed"
            )

            async with self.pool.acquire() as connection:
                async with connection.transaction():
                    await connection.execute(
                        f'UPDATE "order" SET $1 = true WHERE id = $2;',
                        field_to_update,
                        order_id,
                    )

            self.update_queue.task_done()
            logger.success(f"Order {order_id} marked as {field_to_update}.")
