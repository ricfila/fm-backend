import typing

from tortoise import fields
from tortoise.models import Model

if typing.TYPE_CHECKING:
    from backend.database.models import OrderProductIngredient


class OrderProduct(Model):
    """
    The OrderProduct model
    """

    id = fields.IntField(pk=True)
    order = fields.ForeignKeyField(
        model_name="models.Order",
        related_name="order_products",
        on_delete=fields.CASCADE,
        on_update=fields.CASCADE
    )
    product = fields.ForeignKeyField(
        model_name="models.Product",
        on_delete=fields.RESTRICT,
        on_update=fields.CASCADE
    )
    price = fields.DecimalField(max_digits=10, decimal_places=2)
    quantity = fields.IntField()
    notes = fields.CharField(64, null=True)
    variant = fields.ForeignKeyField(
        model_name="models.ProductVariant",
        null=True,
        on_delete=fields.RESTRICT,
        on_update=fields.CASCADE
    )
    order_menu_field = fields.ForeignKeyField(
        model_name="models.OrderMenuField",
        related_name="order_menu_field_products",
        null=True,
        on_delete=fields.CASCADE,
        on_update=fields.CASCADE
    )

    order_menu_field_id: int

    product_id: int
    variant_id: int

    order_product_ingredients: fields.ReverseRelation["OrderProductIngredient"]

    class Meta:
        table = "order_product"

    async def to_dict(
        self,
        include_product: bool = False,
        include_product_dates: bool = False,
        include_product_ingredients: bool = False,
        include_product_roles: bool = False,
        include_product_variants: bool = False,
        include_ingredients: bool = False,
    ) -> dict:
        result = {
            "id": self.id,
            "product_id": self.product_id,
            "price": self.price,
            "quantity": self.quantity,
            "notes": self.notes,
            "variant_id": self.variant_id,
            "order_menu_field_id": self.order_menu_field_id,
        }

        if include_product:
            result["product"] = await self.product.to_dict(
                include_product_dates,
                include_product_ingredients,
                include_product_roles,
                include_product_variants,
            )

        if include_ingredients and hasattr(self, "order_product_ingredients"):
            result["ingredients"] = [
                await ingredient.to_dict()
                for ingredient in self.order_product_ingredients
            ]

        return result
