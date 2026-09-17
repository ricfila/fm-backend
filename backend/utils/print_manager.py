import asyncio
import datetime
import re
import threading

from escpos.printer import Network
from loguru import logger
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from backend.config import Session
from backend.database.models import Printer, Ticket
from backend.database.utils import get_current_time
from backend.utils import PrinterType
from backend.utils.order_text_manager import OrderTextManager

MAX_RETRY_DELAY = 60
PRINTER_TIMEOUT = 5
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
            self.printers[printer_id] = Network(printer_ip_address, timeout=PRINTER_TIMEOUT)
            self._printer_locks[printer_id] = threading.Lock()
    

    def _threaded_print(self, printer: Network, content: str, lock: threading.Lock):
        # Executed in thread with asyncio.to_thread
        with lock:
            # _print_content is already synchronous and does I/O on network
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
            "order__parent_order",
            "order__user",
            "order__confirmed_by"
        ]

        while True:
            # Fetch all ticket that are not printed and not completed
            tickets = (
                await Ticket.filter(
                    printed_at=None,
                    completed_at=None,
                    order__is_deleted=False
                )
                .prefetch_related(*prefetch_values)
            )

            current_time = get_current_time()
            ready_tickets = []
            printed_tickets = []

            for t in tickets:
                if getattr(t.category, "wait_parent_category"):
                    parent_t = await Ticket.filter(
                        order_id=t.order_id,
                        category_id=getattr(t.category, "parent_category_id")
                    ).first()

                    if not parent_t:
                        logger.error(f"Ticket genitore non trovato per l'ordine {t.order_id}")
                        continue
                    
                    trigger_time = getattr(parent_t, "completed_at", None)

                else:
                    if getattr(t.order, "needs_confirmation"):
                        trigger_time = getattr(t.order, "confirmed_at", None)
                    else:
                        trigger_time = getattr(t.order, "created_at")

                
                if trigger_time is None:
                    continue

                if getattr(t.order, "guests") is None and not getattr(t.order, "is_take_away"):
                    # print_delay is forced to 0 for adding orders
                    print_delay = 0
                else:
                    print_delay = getattr(t.category, "print_delay", 0)

                    if getattr(t.order, "needs_confirmation") and not getattr(t.category, "wait_parent_category"):
                        print_delay += Session.settings.delay_after_confirmation

                if trigger_time + datetime.timedelta(seconds=print_delay) <= current_time:
                    ready_tickets.append(t)


            logger.info(f"Trovate {len(ready_tickets)} comande da stampare.")

            for ticket in ready_tickets:
                printed = await self.print_ticket(ticket, update_db=True)
                if printed:
                    printed_tickets.append(ticket)


            logger.debug(
                f"Fine ciclo. Attesa di {RETRY_DELAY} secondi prima del prossimo aggiornamento."
            )

            # Wait for the next update cycle
            await asyncio.sleep(RETRY_DELAY)


    @staticmethod
    def _print_content(printer: Network, content: str, order_id: int = None):
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
                    printer._raw(b"\x1b\x21\x30")
                    printer.text(inner)
                    printer._raw(b"\x1b\x21\x00")
                else:
                    printer.text(part)

        #printer.barcode(str(order_id), "CODE128", height=100, width=3)
        printer.cut()


    async def print_ticket(self, ticket: Ticket, update_db: bool) -> bool:
        logger.debug(
            f"Stampa comanda #{ticket.id} (categoria {ticket.category_id} dell'ordine {ticket.order_id})"
        )

        text = OrderTextManager(ticket.order, ticket.category)
        content = text.generate_text_for_printer(PrinterType.TICKET)

        printer_id = ticket.category.printer_id

        printer = self.printers[printer_id]
        lock = self._printer_locks.get(printer_id, threading.Lock())

        try:
            #self._print_content(printer, content)
            await asyncio.to_thread(self._threaded_print, printer, content, lock)

            # Saving printed state of ticket
            if update_db:
                ticket.printed_at = get_current_time()
                await ticket.save()
            
            return True

        except Exception as e:
            logger.error(
                f"Errore di stampa su {printer.host} → comanda #{ticket.id} (categoria {ticket.category_id} dell'ordine {ticket.order_id})"
            )
            logger.exception(e)

            return False
