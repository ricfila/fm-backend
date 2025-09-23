from tortoise import fields
from tortoise.models import Model


class ProductVariant(Model):
    """
    The ProductVariant model
    """

    id = fields.IntField(pk=True)
    name = fields.CharField(32)
    price = fields.FloatField()
    is_deleted = fields.BooleanField(default=False)
    product = fields.ForeignKeyField(
        model_name="models.Product",
        related_name="variants",
        on_delete=fields.CASCADE,
        on_update=fields.CASCADE
    )

    product_id: int

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
