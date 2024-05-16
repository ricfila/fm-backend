from tortoise import fields
from tortoise.models import Model


class ProductVariant(Model):
    """
    The ProductVariant model
    """

    id = fields.IntField(pk=True)
    name = fields.CharField(32, unique=True)
    price = fields.FloatField()
    product = fields.ForeignKeyField("models.Product", "variants")

    class Meta:
        table = "product_variant"
        unique_together = ("name", "product_id")

    async def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "product_id": self.product_id,
        }
