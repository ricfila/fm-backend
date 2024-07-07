import typing

from tortoise import fields
from tortoise.models import Model

if typing.TYPE_CHECKING:
    from backend.database.models import OrderMenuField


class OrderMenu(Model):
    """
    The OrderMenu model
    """

    id = fields.IntField(pk=True)
    menu = fields.ForeignKeyField("models.Menu", related_name="order_menus")
    price = fields.FloatField()
    quantity = fields.IntField()

    menu_id: int

    order_menu_fields: fields.ReverseRelation["OrderMenuField"]

    class Meta:
        table = "order_menu"

    async def to_dict(self):
        return {
            "id": self.id,
            "menu_id": self.menu_id,
            "price": self.price,
            "fields": [
                await field.to_dict() for field in self.order_menu_fields
            ],
        }
