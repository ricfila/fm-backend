from tortoise import fields
from tortoise.models import Model


class OrderProductIngredient(Model):
    """
    The OrderProductIngredient model
    """

    id = fields.IntField(pk=True)
    order_product = fields.ForeignKeyField(
        "models.OrderProduct", related_name="order_product_ingredients"
    )
    product_ingredient = fields.ForeignKeyField("models.ProductIngredient")

    order_product_id: int
    product_ingredient_id: int

    class Meta:
        table = "order_product_ingredient"
        unique_together = ("order_product_id", "product_ingredient_id")

    async def get_ingredient(self) -> int:
        return self.product_ingredient_id

    async def to_dict(self) -> dict:
        return {
            "id": self.id,
            "order_product_id": self.order_product_id,
            "product_ingredient_id": self.product_ingredient_id,
        }
