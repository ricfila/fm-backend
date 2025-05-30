import asyncio
import re

from escpos.printer import Network
from loguru import logger

from backend.database.models import Order, Printer, OrderPrinter
from backend.utils import PrinterType
from backend.utils.order_text_manager import OrderTextManager

RETRY_DELAY = 5


class PrintManager:
    def __init__(self):
        self.printers: dict[int, Network] = {}

    @classmethod
    async def create(cls):
        new_obj = cls()
        printers = await Printer.all()

        for printer in printers:
            new_obj.add_printer(printer.id, printer.ip_address)

        return new_obj

    def add_printer(self, printer_id: int, printer_ip_address: str):
        if printer_id not in self.printers:
            self.printers[printer_id] = Network(printer_ip_address, timeout=5)
            asyncio.create_task(self._worker(printer_id))

    @staticmethod
    async def get_first_order_to_print(
        printer_id: int,
    ) -> tuple[Order, PrinterType, int] | None:
        prefetch_values = [
            "order_menus__order_menu_fields__order_menu_field_products__order_product_ingredients__product_ingredient",
            "order_menus__menu",
            "order_products__order_product_ingredients__product_ingredient",
            "order_products__variant",
            "user__role__printers__printer",
            "user__role__order_confirmer__printers__printer",
            "order_printers__role_printer__printer",
            "confirmed_by__role__printers__printer",
        ]

        orders = (
            await Order.filter(is_done=False)
            .order_by("created_at")
            .prefetch_related(*prefetch_values)
        )

        for order in orders:
            user_role_printers = list(order.user.role.printers)
            confirmed_by_role_printers = list(
                order.user.role.order_confirmer.printers
            )

            user_role_printer_ids = {x.id for x in user_role_printers}
            role_printer_ids = {
                x.id: x
                for x in user_role_printers + confirmed_by_role_printers
            }
            order_role_printer_ids = {
                x.role_printer_id for x in order.order_printers
            }
            order_roles_to_print = (
                set(role_printer_ids.keys()) - order_role_printer_ids
            )

            if not order_roles_to_print:
                order.is_done = True
                await order.save()

                continue

            ordered_roles_to_print = {
                x
                for x in user_role_printer_ids
                if x not in order_role_printer_ids
            }

            if order.is_take_away or order.is_confirm:
                ordered_roles_to_print = sorted(
                    order_roles_to_print,
                    key=lambda x: (x not in user_role_printer_ids, x),
                )

            for role_printer in ordered_roles_to_print:
                if role_printer_ids.get(role_printer).printer_id == printer_id:
                    return (
                        order,
                        role_printer_ids.get(role_printer).printer_type,
                        role_printer,
                    )

        return None

    async def _worker(self, printer_id: int):
        printer = self.printers[printer_id]

        while True:
            result = await self.get_first_order_to_print(printer_id)

            if not result:
                await asyncio.sleep(RETRY_DELAY)
                continue

            order, printer_type, role_printer_id = result

            text = OrderTextManager(order)
            content = await text.generate_text_for_printer(printer_type)

            print(content)

            try:
                await asyncio.to_thread(self._print_content, printer, content)

                logger.success(
                    f"Successfully printed {order.id} on {printer.host}"
                )

                await OrderPrinter.create(
                    order_id=order.id, role_printer_id=role_printer_id
                )
                logger.success(f"Order {order.id} marked as printed.")
            except Exception as e:
                logger.error(f"Print error on {printer.host}")
                logger.exception(e)
                await asyncio.sleep(RETRY_DELAY)
                continue

    @staticmethod
    def _print_content(printer: Network, content: str):
        printer.open()
        for line in re.split(r"(?<=\n)", content):
            printer.set(align="left", font="a")
            printer.text(line)
        printer.cut()
