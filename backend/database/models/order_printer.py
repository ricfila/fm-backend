from tortoise import fields
from tortoise.models import Model


class OrderPrinter(Model):
    """
    The OrderPrinter model
    """

    id = fields.IntField(pk=True)
    order = fields.ForeignKeyField(
        model_name="models.Order",
        related_name="order_printers",
        on_delete=fields.CASCADE,
        on_update=fields.CASCADE
    )
    role_printer = fields.ForeignKeyField(
        model_name="models.RolePrinter",
        on_delete=fields.RESTRICT,
        on_update=fields.CASCADE
    )

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
