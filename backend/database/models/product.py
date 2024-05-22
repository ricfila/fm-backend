import typing

from tortoise import fields
from tortoise.models import Model

from backend.utils import Category

if typing.TYPE_CHECKING:
    from backend.database.models import (
        ProductVariant,
        ProductRole,
        ProductDate,
        ProductIngredient,
    )


class Product(Model):
    """
    The Product model
    """

    id = fields.IntField(pk=True)
    name = fields.CharField(32, unique=True)
    short_name = fields.CharField(20, unique=True)
    is_priority = fields.BooleanField(default=False)
    price = fields.FloatField()
    category = fields.CharEnumField(Category)
    subcategory = fields.ForeignKeyField(
        "models.Subcategory", related_name="subcategory_id"
    )

    subcategory_id: int

    dates: fields.ReverseRelation["ProductDate"]
    ingredients: fields.ReverseRelation["ProductIngredient"]
    roles: fields.ReverseRelation["ProductRole"]
    variants: fields.ReverseRelation["ProductVariant"]

    class Meta:
        table = "product"

    async def to_dict_name(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "short_name": self.short_name,
        }

    async def to_dict(
        self,
        include_dates: bool = False,
        include_ingredients: bool = False,
        include_roles: bool = False,
        include_variants: bool = False,
    ):
        await self.fetch_related("dates", "ingredients", "roles", "variants")

        result = {
            "id": self.id,
            "name": self.name,
            "short_name": self.short_name,
            "is_priority": self.is_priority,
            "price": self.price,
            "category": self.category,
            "subcategory_id": self.subcategory_id,
        }

        if include_dates:
            result["dates"] = [await date.to_dict() for date in self.dates]

        if include_ingredients:
            result["ingredients"] = [
                await ingredient.to_dict() for ingredient in self.ingredients
            ]

        if include_roles:
            result["roles"] = [await role.to_dict() for role in self.roles]

        if include_variants:
            result["variants"] = [
                await variant.to_dict() for variant in self.variants
            ]

        return result
