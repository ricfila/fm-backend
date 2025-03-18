from tortoise import fields
from tortoise.models import Model


class Setting(Model):
    """
    The Setting model
    """

    id = fields.IntField(pk=True)
    order_requires_confirmation = fields.BooleanField(default=False)

    class Meta:
        name = "setting"

    async def to_dict(self) -> dict:
        return {
            "order_requires_confirmation": self.order_requires_confirmation,
        }
