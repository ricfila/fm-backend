import asyncio
import datetime
import pytz
import re
import threading

from escpos.printer import Network
from loguru import logger
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from backend.database.models import Order, Printer, Ticket
from backend.models.error import Conflict
from backend.utils import ErrorCodes, PrinterType
from backend.utils.order_text_manager import OrderTextManager

MAX_RETRY_DELAY = 60
RETRY_DELAY = 10
STEP = 2


class PrintManager:
    def __init__(self):
        self.printers: dict[int, Network] = {}
        self._printer_locks: dict[int, threading.Lock] = {}
    
    
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
            self._printer_locks[printer_id] = threading.Lock()
    

    def _threaded_print(self, printer: Network, content: str, lock: threading.Lock):
        # Eseguito in thread tramite asyncio.to_thread
        with lock:
            # _print_content è già sincrona e fa I/O di rete
            self._print_content(printer, content)
            return True


    async def update_worker(self):
        prefetch_values = [
            "category__printer",
            "order__order_products__product__subcategory",
            "order__order_products__order_product_ingredients__ingredient",
            "order__order_products__variant",
            "order__order_menus__order_menu_fields__order_menu_field_products__order_product_ingredients__ingredient",
            "order__order_menus__menu",
            "order__user",
            "order__confirmed_by"
        ]

        while True:
            tickets = (
                await Ticket.filter(
                    printed_at=None,
                    order__is_done=False,
                    order__confirmed_at__isnull=False
                )
                .prefetch_related(*prefetch_values)
            )

            rome_tz = pytz.timezone("Europe/Rome")
            now_in_rome = datetime.datetime.now(rome_tz)

            ready_tickets = []
            printed_tickets = []

            for t in tickets:
                confirmed_at = getattr(t.order, "confirmed_at", None)
                print_delay = getattr(t.category, "print_delay", 0) or 0

                if confirmed_at is None:
                    continue

                if confirmed_at + datetime.timedelta(seconds=print_delay) <= now_in_rome:
                    ready_tickets.append(t)


            logger.info(f"Trovate {len(ready_tickets)} comande da stampare.")

            for ticket in ready_tickets:
                printed = await self.print_ticket(ticket, update_db=True)
                if printed:
                    printed_tickets.append(ticket)
                

            # Set is_done=True for completed orders in this cycle
            async with in_transaction() as connection:
                orders = await Order.filter(
                    id__in=[t.order_id for t in printed_tickets],
                    is_done=False
                ).prefetch_related("order_tickets").using_db(connection)

                for order in orders:
                    tickets_to_print = len([t for t in order.order_tickets if t.printed_at == None])
                    if tickets_to_print == 0:
                        order.is_done = True
                    else:
                        orders.remove(order)
                
                if len(orders) > 0:
                    try:
                        await Order.bulk_update(orders, fields=['is_done'], using_db=connection)
                    except IntegrityError:
                        raise Conflict(code=ErrorCodes.ORDER_UPDATE_FAILED)


            logger.debug(
                f"Fine ciclo. Attesa di {RETRY_DELAY} secondi prima del prossimo aggiornamento."
            )
            await asyncio.sleep(RETRY_DELAY)


    @staticmethod
    def _print_content(printer: Network, content: str):
        printer.open()
        printer.hw("INIT")
        printer.charcode("CP850")
        printer.buzzer(times=3, duration=1)

        content = content.replace("\r\n", "\n").replace("\r", "\n")
        for line in content.splitlines(keepends=True):
            printer.set(align="left", font="a",)

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


    async def print_ticket(self, ticket: Ticket, update_db: bool) -> bool:
        logger.debug(
            f"Stampa comanda #{ticket.id} (categoria {ticket.category_id} dell'ordine {ticket.order_id})"
        )

        text = OrderTextManager(ticket.order, ticket.category)
        content = text.generate_text_for_printer(PrinterType.TICKET)

        # TODO: it has to moved into database
        if ticket.category_id != 3 and ticket.category_id != 5:
            content += "\n* Con POLENTA (2 fette)\n# Con PATATINE (1 porzione)\n"

        printer_id = ticket.category.printer_id
        if printer_id is None:
            return True

        printer = self.printers[printer_id]
        lock = self._printer_locks.get(printer_id, threading.Lock())

        try:
            #self._print_content(printer, content)
            await asyncio.to_thread(self._threaded_print, printer, content, lock)

            # Saving printed state of ticket
            if update_db:
                rome_tz = pytz.timezone("Europe/Rome")
                ticket.printed_at = datetime.datetime.now(rome_tz)
                await ticket.save()
            
            return True

        except Exception as e:
            logger.error(
                f"Errore di stampa su {printer.host} → comanda #{ticket.id} (categoria {ticket.category_id} dell'ordine {ticket.order_id})"
            )
            logger.exception(e)

            return False
