from tortoise import fields
from tortoise.models import Model


class ProductRole(Model):
    """
    The ProductRole model
    """

    id = fields.IntField(pk=True)
    role = fields.ForeignKeyField("models.Role")
    product = fields.ForeignKeyField("models.Product")

    class Meta:
        table = "product_role"
        unique_together = ("role_id", "product_id")

    async def to_dict(self):
        return {
            "id": self.id,
            "role_id": self.role_id,
            "product_id": self.product_id,
        }
