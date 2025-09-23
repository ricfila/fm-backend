import typing

from tortoise import fields
from tortoise.models import Model

if typing.TYPE_CHECKING:
    from backend.database.models import OrderProduct


class OrderMenuField(Model):
    """
    The OrderMenuField model
    """

    id = fields.IntField(pk=True)
    order_menu = fields.ForeignKeyField(
        model_name="models.OrderMenu",
        related_name="order_menu_fields",
        on_delete=fields.CASCADE,
        on_update=fields.CASCADE
    )
    menu_field = fields.ForeignKeyField(
        model_name="models.MenuField",
        on_delete=fields.RESTRICT,
        on_update=fields.CASCADE
    )

    order_menu_id: int
    menu_field_id: int

    order_menu_field_products: fields.ReverseRelation["OrderProduct"]

    class Meta:
        table = "order_menu_field"
        unique_together = ("order_menu_id", "menu_field_id")

    async def to_dict(
        self,
        include_products: bool = False,
        include_products_ingredients: bool = False,
    ) -> dict:
        result = {
            "id": self.id,
            "order_menu_id": self.order_menu_id,
            "menu_field_id": self.menu_field_id,
        }

        if include_products and hasattr(self, "order_menu_field_products"):
            result["products"] = [
                await product.to_dict(
                    include_ingredients=include_products_ingredients
                )
                for product in self.order_menu_field_products
            ]

        return result
