from tortoise import fields
from tortoise.models import Model


class ProductIngredient(Model):
    """
    The ProductIngredient model
    """

    id = fields.IntField(pk=True)
    product = fields.ForeignKeyField("models.Product", related_name="ingredients")
    ingredient = fields.ForeignKeyField("models.Ingredient")
    price = fields.DecimalField(max_digits=10, decimal_places=2)
    max_quantity = fields.DecimalField(max_digits=10, decimal_places=2, default=1)
    is_default = fields.BooleanField(default=True)
    is_deleted = fields.BooleanField(default=False)

    product_id: int
    ingredient_id: int

    class Meta:
        table = "product_ingredient"
        unique_together = ("product_id", "ingredient_id")

    async def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "ingredient_id": self.ingredient_id,
            "price": self.price,
            "max_quantity": self.max_quantity,
            "is_default": self.is_default
        }
    
    async def to_dict_name(self):
        ingredient_name = (await self.ingredient).name if hasattr(self, "ingredient") else None

        return {
            "id": self.id,
            "ingredient_id": self.ingredient_id,
            "name": ingredient_name,
            "price": self.price,
            "max_quantity": self.max_quantity,
            "is_default": self.is_default
        }
