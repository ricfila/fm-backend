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
    product = fields.ForeignKeyField("models.Product")
    price = fields.FloatField()
    quantity = fields.IntField()
    variant = fields.ForeignKeyField("models.ProductVariant", null=True)
    order = fields.ForeignKeyField("models.Order", "order_products")
    order_menu_field = fields.ForeignKeyField(
        "models.OrderMenuField", "order_menu_field_products", null=True
    )

    product_id: int
    variant_id: int

    order_product_ingredients: fields.ReverseRelation["OrderProductIngredient"]

    class Meta:
        table = "order_product"

    async def to_dict(self):
        await self.fetch_related("order_product_ingredients")

        return {
            "id": self.id,
            "product_id": self.product_id,
            "variant_id": self.variant_id,
            "ingredients": [
                await ingredient.get_ingredient()
                for ingredient in self.order_product_ingredients
            ],
            "price": self.price,
        }
