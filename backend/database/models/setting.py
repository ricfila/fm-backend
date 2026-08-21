from tortoise import fields
from tortoise.models import Model


class Setting(Model):
    """
    The Setting model
    """

    id = fields.IntField(pk=True)
    order_requires_confirmation = fields.BooleanField(default=False)
    receipt_header = fields.TextField(default="")
    cover_charge = fields.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    max_guests_for_main_products = fields.IntField(default=None, null=True)

    class Meta:
        name = "setting"

    async def to_dict(self) -> dict:
        return {
            "order_requires_confirmation": self.order_requires_confirmation,
            "receipt_header": self.receipt_header,
            "cover_charge": self.cover_charge,
            "max_guests_for_main_products": self.max_guests_for_main_products,
        }
