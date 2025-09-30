import typing

from tortoise import fields
from tortoise.models import Model

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
    name = fields.CharField(64, unique=True)
    short_name = fields.CharField(20, unique=True)
    is_priority = fields.BooleanField(default=False)
    is_main = fields.BooleanField(default=True)
    price = fields.FloatField()
    category = fields.ForeignKeyField(
        model_name="models.Category",
        on_delete=fields.RESTRICT,
        on_update=fields.CASCADE
    )
    subcategory = fields.ForeignKeyField(
        model_name="models.Subcategory",
        on_delete=fields.RESTRICT,
        on_update=fields.CASCADE
    )
    order = fields.IntField(default=0)
    daily_max_sales = fields.IntField(null=True)
    color = fields.CharField(7, null=True, default=None)

    category_id: int
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
        include_subcategory: bool = False,
        include_variants: bool = False,
    ):
        # Build the base result
        result = {
            "id": self.id,
            "name": self.name,
            "short_name": self.short_name,
            "is_priority": self.is_priority,
            "is_main": self.is_main,
            "price": self.price,
            "category_id": self.category_id,
            "subcategory_id": self.subcategory_id,
            "order": self.order,
            "daily_max_sales": self.daily_max_sales,
            "color": self.color
        }

        # Add dates if pre-fetched and requested
        if include_dates and hasattr(self, "dates"):
            result["dates"] = [await date.to_dict() for date in self.dates]

        # Add ingredients if pre-fetched and requested
        if include_ingredients and hasattr(self, "ingredients"):
            result["ingredients"] = [
                await ingredient.to_dict_name() for ingredient in self.ingredients
            ]

        # Add roles if pre-fetched and requested
        if include_roles and hasattr(self, "roles"):
            result["roles"] = [await role.to_dict() for role in self.roles]

        # Add subcategory if pre-fetched and requested
        if include_subcategory and hasattr(self, "subcategory"):
            subcategory = await self.subcategory
            result["subcategory"] = await subcategory.to_dict()

        # Add variants if pre-fetched and requested
        if include_variants and hasattr(self, "variants"):
            result["variants"] = [
                await variant.to_dict() for variant in self.variants
            ]

        return result
