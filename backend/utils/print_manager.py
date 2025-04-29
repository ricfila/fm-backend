import asyncio
import collections

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
    def __init__(self):
        self.queues = collections.defaultdict(asyncio.Queue)
        self.printers: dict[int, Network] = {}

    def add_printer(self, printer_id: int, printer_ip_address: str):
        self.printers[printer_id] = Network(printer_ip_address, timeout=5)
        asyncio.create_task(self._worker(printer_id))

    async def _worker(self, printer_id: int):
        queue = self.queues[printer_id]
        printer = self.printers[printer_id]

        while True:
            job = await queue.get()
            content = job["content"]

            while True:
                try:
                    for x in content.split("\n"):
                        printer.set(align="left", font="a")
                        printer.text(x if x else "\n")
                    printer.cut()
                except Exception as e:
                    logger.error(f"Print error on {printer.host}: {e}")
                    await asyncio.sleep(RETRY_DELAY)

                    continue

                logger.success(f"Successfully printed on {printer.host}")
                break

            queue.task_done()

    async def add_job(self, order_id: int, connection: BaseDBAsyncClient):
        order = await get_order(order_id, connection)

        if not order:
            return

        text = OrderTextManager(order)

        for role_printer in order.user.role.printers:
            p = role_printer.printer
            if p.id not in self.printers:
                self.add_printer(p.id, p.ip_address)

            content = await text.generate_text_for_printer(
                role_printer.printer_type
            )

            await self.queues[p.id].put({"content": content})
