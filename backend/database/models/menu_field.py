import typing

from tortoise import fields
from tortoise.models import Model

if typing.TYPE_CHECKING:
    from backend.database.models import MenuFieldProduct


class MenuField(Model):
    """
    The MenuField model
    """

    id = fields.IntField(pk=True)
    name = fields.CharField(32)
    max_sortable_elements = fields.IntField()
    additional_cost = fields.FloatField()
    is_optional = fields.BooleanField(default=False)
    can_exceed_max_sortable = fields.BooleanField(default=False)
    menu = fields.ForeignKeyField("models.Menu", "menu_fields")

    menu_id: int

    field_products: fields.ReverseRelation["MenuFieldProduct"]

    class Meta:
        table = "menu_field"
        unique_together = ("name", "menu_id")

    async def to_dict(
        self,
        include_fields_products: bool = False,
        include_fields_products_dates: bool = False,
        include_fields_products_ingredients: bool = False,
        include_fields_products_roles: bool = False,
        include_fields_products_variants: bool = False,
    ) -> dict:
        result = {
            "id": self.id,
            "name": self.name,
            "max_sortable_elements": self.max_sortable_elements,
            "additional_cost": self.additional_cost,
            "is_optional": self.is_optional,
            "menu_id": self.menu_id,
        }

        if include_fields_products and hasattr(self, "field_products"):
            result["products"] = [
                await product.to_dict(
                    include_fields_products_dates,
                    include_fields_products_ingredients,
                    include_fields_products_roles,
                    include_fields_products_variants,
                )
                for product in self.field_products
            ]

        return result
