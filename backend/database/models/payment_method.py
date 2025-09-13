from tortoise import fields
from tortoise.models import Model


class PaymentMethod(Model):
    """
    The PaymentMethod model
    """

    id = fields.IntField(pk=True)
    name = fields.CharField(32, unique=True)
    order = fields.IntField(default=0)
    is_deleted = fields.BooleanField(default=False)

    class Meta:
        table = "payment_method"

    async def to_dict_name(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
        }

    async def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "order": self.order,
            "is_deleted": self.is_deleted
        }
