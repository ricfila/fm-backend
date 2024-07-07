import typing

from tortoise import fields
from tortoise.models import Model

if typing.TYPE_CHECKING:
    from backend.database.models import OrderMenu, OrderProduct


class Order(Model):
    """
    The Order model
    """

    id = fields.IntField(pk=True)
    customer = fields.CharField(32)
    guests = fields.IntField(null=True)
    is_take_away = fields.BooleanField()
    table = fields.IntField(null=True)
    user = fields.ForeignKeyField("models.User")
    created_at = fields.DatetimeField(auto_now_add=True)

    user_id: int

    order_menus: fields.ReverseRelation["OrderMenu"]
    order_products: fields.ReverseRelation["OrderProduct"]

    class Meta:
        table = "order"

    async def to_dict(self) -> dict:
        await self.fetch_related("order_menus", "order_products")

        return {
            "id": self.id,
            "customer": self.customer,
            "guests": self.guests,
            "is_take_away": self.is_take_away,
            "table": self.table,
            "user_id": self.user_id,
            "created_at": self.created_at,
            "menus": [await menu.to_dict() for menu in self.order_menus],
            "products": [
                await product.to_dict() for product in self.order_products
            ],
        }
