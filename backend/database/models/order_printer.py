from tortoise import fields
from tortoise.models import Model


class OrderPrinter(Model):
    """
    The OrderPrinter model
    """

    id = fields.IntField(pk=True)
    order = fields.ForeignKeyField("models.Order", "order_printers")
    role_printer = fields.ForeignKeyField("models.RolePrinter")

    order_id: int
    role_printer_id: int

    class Meta:
        table = "order_printer"
        unique_together = ("order_id", "role_printer_id")

    async def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "printer_id": self.role_printer_id,
        }
