from tortoise import fields
from tortoise.models import Model


class ProductIngredient(Model):
    """
    The ProductIngredient model
    """

    id = fields.IntField(pk=True)
    name = fields.CharField(32, unique=True)
    price = fields.FloatField()
    product_id = fields.ForeignKeyField("models.Product")

    class Meta:
        table = "product_ingredient"
        unique_together = ("name", "product_id")

    async def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "product_id": self.product_id,
        }
