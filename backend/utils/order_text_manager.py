from backend.database.models import Order
from backend.utils import PrinterType


class OrderTextManager:
    def __init__(self, order: Order):
        self.order = order

    async def _render_receipt_text(self):
        receipt_text = ""

        receipt_number = f"Scontrino n. {self.order.id}"
        receipt_date = self.order.created_at.strftime("%d/%m/%Y %H:%M")
        receipt_text += f"{receipt_number:<22}{receipt_date:>20}\n\n"

        return receipt_text

    async def generate_text_for_printer(self, printer_type: PrinterType):
        printer_formatters = {
            PrinterType.RECEIPT: self._render_receipt_text,
        }

        return await printer_formatters[printer_type]()
