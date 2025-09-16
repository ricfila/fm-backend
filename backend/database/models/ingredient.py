import typing

from tortoise import fields
from tortoise.models import Model

if typing.TYPE_CHECKING:
    from backend.database.models import OrderProductIngredient
    from backend.database.models import ProductIngredient


class Ingredient(Model):
    """
    The Ingredient model
    """

    id = fields.IntField(pk=True)
    name = fields.CharField(32, unique=True)
    ward = fields.CharField(32)
    is_deleted = fields.BooleanField(default=False)

    order_product_ingredients_ingredient: fields.ReverseRelation["OrderProductIngredient"]
    product_ingredient: fields.ReverseRelation["ProductIngredient"]

    class Meta:
        table = "ingredient"

    async def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "ward": self.ward
        }
    
    async def to_dict_name(self) -> dict:
        return {
            "id": self.id,
            "name": self.name
        }
