from tortoise import fields
from tortoise.models import Model


class OrderProductIngredient(Model):
    """
    The OrderProductIngredient model
    """

    id = fields.IntField(pk=True)
    order_product = fields.ForeignKeyField("models.OrderProduct", related_name="order_product_ingredients")
    ingredient = fields.ForeignKeyField("models.Ingredient", related_name="order_product_ingredients_ingredient")
    quantity = fields.DecimalField(max_digits=10, decimal_places=2)

    order_product_id: int
    ingredient_id: int

    class Meta:
        table = "order_product_ingredient"
        unique_together = ("order_product_id", "ingredient_id")

    async def to_dict(self) -> dict:
        result = {
            "id": self.id,
            "order_product_id": self.order_product_id,
            "product_ingredient_id": self.ingredient_id,
            "quantity": self.quantity,
        }

        return result
