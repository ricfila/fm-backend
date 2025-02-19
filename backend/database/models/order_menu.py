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
    menu = fields.ForeignKeyField("models.Menu")
    price = fields.FloatField()
    quantity = fields.IntField()
    order = fields.ForeignKeyField("models.Order", "order_menus")

    menu_id: int

    order_menu_fields: fields.ReverseRelation["OrderMenuField"]

    class Meta:
        table = "order_menu"

    async def to_dict(self, include_menus_fields: bool = False, include_menus_fields_products: bool = False) -> dict:
        result =  {
            "id": self.id,
            "menu_id": self.menu_id,
            "price": self.price,
            "quantity": self.quantity,
        }

        if include_menus_fields and hasattr(self, "order_menu_fields"):
            result["fields"] = [await field.to_dict(include_menus_fields_products) for field in self.order_menu_fields]

        return result
