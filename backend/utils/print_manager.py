import asyncio
import re

from escpos.printer import Network
from loguru import logger

from backend.database.models import Order, Printer, OrderPrinter
from backend.utils import PrinterType
from backend.utils.order_text_manager import OrderTextManager

MAX_RETRY_DELAY = 60
RETRY_DELAY = 10
STEP = 2


class PrintManager:
    def __init__(self):
        self.printers: dict[int, Network] = {}
    
    
    @classmethod
    async def create(cls):
        new_obj = cls()
        printers = await Printer.all()

        for printer in printers:
            new_obj.add_printer(printer.id, printer.ip_address)

        asyncio.create_task(new_obj.update_worker())

        return new_obj

    
    def add_printer(self, printer_id: int, printer_ip_address: str):
        if printer_id not in self.printers:
            self.printers[printer_id] = Network(printer_ip_address, timeout=5)
    

    async def update_worker(self):
        prefetch_values = [
            "order_menus__order_menu_fields__order_menu_field_products__order_product_ingredients__ingredient",
            "order_menus__menu",
            "order_products__order_product_ingredients__ingredient",
            "order_products__variant",
            "user__role__printers__printer",
            "user__role__order_confirmer__printers__printer",
            "order_printers__role_printer__printer",
            "confirmed_by__role__printers__printer",
            "parent_order",
        ]

        while True:
            orders = (
                await Order.filter(is_done=False)
                .order_by("created_at")
                .prefetch_related(*prefetch_values)
            )
            logger.info(f"Trovati {len(orders)} ordini attivi da processare.")

            for order in orders:
                logger.debug(
                    f"Elaborazione ordine #{order.id} (Creato il {order.created_at})"
                )
                user_role_printers = list(order.user.role.printers)
                confirmed_by_role_printers = []
                if order.user.role.order_confirmer:
                    if order.user.role.order_confirmer.printers:
                        confirmed_by_role_printers = list(
                            order.user.role.order_confirmer.printers
                        )
                        logger.debug(
                            f"Ordine #{order.id}: trovati {len(confirmed_by_role_printers)} stampanti per il ruolo di conferma."
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
                logger.debug(
                    f"Ordine #{order.id}: ruoli da stampare → {order_roles_to_print}"
                )

                if order.is_take_away:
                    logger.debug(
                        f"Ordine #{order.id} è da asporto, rimozione stampanti per bevande..."
                    )
                    order_roles_to_print -= {
                        x
                        for x in order_roles_to_print
                        if role_printer_ids.get(x).printer_type
                        == PrinterType.DRINKS
                    }

                if not order_roles_to_print:
                    logger.info(
                        f"Ordine #{order.id} già stampato da tutti i ruoli necessari. Lo segno come completato."
                    )
                    order.is_done = True
                    await order.save()

                    for rp in role_printer_ids.keys():
                        self.in_progress.discard((order.id, rp))

                    continue

                ordered_roles_to_print = {
                    x
                    for x in user_role_printer_ids
                    if x not in order_role_printer_ids
                }

                if order.is_confirmed:
                    logger.debug(
                        f"Ordine #{order.id} è confermato o da asporto: applico priorità ai ruoli dell'utente."
                    )
                    ordered_roles_to_print = sorted(
                        order_roles_to_print,
                        key=lambda x: (x not in user_role_printer_ids, x),
                    )

                for role_printer in ordered_roles_to_print:
                    rp = role_printer_ids.get(role_printer)
                    key = (order.id, rp.id)

                    if key in self.in_progress:
                        logger.debug(
                            f"Ordine #{order.id} → Ruolo #{rp.id} → Stampante #{rp.printer_id} già in coda, salto."
                        )
                        continue

                    logger.info(
                        f"Inserisco in coda: Ordine #{order.id} → Ruolo #{rp.id} → Stampante #{rp.printer_id}"
                    )
                    self.in_progress.add(key)
                    await self.queues[rp.printer_id].put((order, rp))

            logger.debug(
                f"Fine ciclo. Attesa di {RETRY_DELAY} secondi prima del prossimo aggiornamento."
            )
            await asyncio.sleep(RETRY_DELAY)


    @staticmethod
    def _print_content(printer: Network, content: str):
        printer.open()
        for line in re.split(r"(?<=\n)", content):
            printer.set(align="left", font="a")

            parts = re.split(r"(<DOUBLE>.*?</DOUBLE>)", line)
            for part in parts:
                if part.startswith("<DOUBLE>") and part.endswith("</DOUBLE>"):
                    inner = part[len("<DOUBLE>") : -len("</DOUBLE>")]
                    printer._raw(b"\x1B\x21\x30")
                    printer.text(inner)
                    printer._raw(b"\x1B\x21\x00")
                else:
                    printer.text(part)

        printer.cut()

    async def add_job(self, order: Order, printer_types: list[PrinterType]):
        printers = list(order.user.role.printers)
        printers_confirmed = (
            list(order.user.role.order_confirmer.printers)
            if order.is_confirmed or order.is_take_away
            else []
        )

        printers_to_print = [
            p
            for p in (printers + printers_confirmed)
            if p.printer_type in printer_types
        ]

        for role_printer in printers_to_print:
            await self.queues[role_printer.printer_id].put(
                (order, role_printer)
            )
