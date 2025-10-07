import typing

from tortoise import fields
from tortoise.models import Model

if typing.TYPE_CHECKING:
    from backend.database.models import OrderProductIngredient
    from backend.database.models import ProductIngredient
    from backend.database.models import Stock


class Ingredient(Model):
    """
    The Ingredient model
    """

    id = fields.IntField(pk=True)
    name = fields.CharField(32, unique=True)
    ward = fields.CharField(32)
    is_deleted = fields.BooleanField(default=False)
    is_monitored = fields.BooleanField(default=True)
    sell_if_stocked = fields.BooleanField(default=False)
    cooking_time = fields.IntField(null=True, default=None)
    target_quantity = fields.DecimalField(max_digits=10, decimal_places=2, null=True, default=None)

    order_product_ingredients_ingredient: fields.ReverseRelation["OrderProductIngredient"]
    product_ingredient: fields.ReverseRelation["ProductIngredient"]
    stock: fields.ReverseRelation["Stock"]

    class Meta:
        table = "ingredient"

    async def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "ward": self.ward,
            "is_monitored": self.is_monitored,
            "sell_if_stocked": self.sell_if_stocked,
            "cooking_time": self.cooking_time,
            "target_quantity": self.target_quantity,
        }
    
    async def to_dict_name(self) -> dict:
        return {
            "id": self.id,
            "name": self.name
        }
