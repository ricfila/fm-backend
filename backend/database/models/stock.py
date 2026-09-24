from tortoise import fields
from tortoise.models import Model


class Stock(Model):
    """
    The Stock model
    """

    id = fields.IntField(pk=True)
    ingredient = fields.ForeignKeyField(
        to="models.Ingredient",
        related_name="ingredient_stock",
        on_delete=fields.CASCADE
    )
    quantity = fields.DecimalField(max_digits=10, decimal_places=2)
    available_from = fields.DatetimeField(db_default=fields.Now())
    is_valid = fields.BooleanField(db_default=True)

    ingredient_id: int

    class Meta:
        table = "stock"

    async def to_dict(self) -> dict:
        return {
            "id": self.id,
            "ingredient_id": self.ingredient_id,
            "quantity": self.quantity,
            "available_from": self.available_from,
            "is_valid": self.is_valid
        }
