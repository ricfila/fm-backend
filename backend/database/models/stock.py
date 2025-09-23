from tortoise import fields
from tortoise.models import Model


class Stock(Model):
    """
    The Stock model
    """

    id = fields.IntField(pk=True)
    ingredient = fields.ForeignKeyField(
        model_name="models.Ingredient",
        on_delete=fields.CASCADE,
        on_update=fields.CASCADE
    )
    quantity = fields.DecimalField(max_digits=10, decimal_places=2)
    available_from = fields.DatetimeField(auto_now_add=True)
    is_last_stock = fields.BooleanField(default=False)

    ingredient_id: int

    class Meta:
        table = "stock"

    async def to_dict(self) -> dict:
        return {
            "id": self.id,
            "ingredient_id": self.ingredient_id,
            "quantity": self.quantity,
            "available_from": self.available_from,
            "is_last_stock": self.is_last_stock
        }
