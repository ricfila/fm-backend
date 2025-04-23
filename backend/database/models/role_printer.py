from tortoise import fields
from tortoise.models import Model

from backend.utils import PrinterType


class RolePrinter(Model):
    """
    The RolePrinter model
    """

    id = fields.IntField(pk=True)
    role = fields.ForeignKeyField("models.Role", "printers")
    printer = fields.ForeignKeyField("models.Printer")
    printer_type = fields.CharEnumField(PrinterType)

    role_id: int
    printer_id: int

    class Meta:
        table = "role_printer"
        unique_together = ("role_id", "printer_id")

    async def to_dict(self):
        return {
            "id": self.id,
            "role_id": self.role_id,
            "printer_id": self.printer_id,
            "printer_type": self.printer_type,
        }
