from tortoise import fields
from tortoise.models import Model


class ProductRole(Model):
    """
    The ProductRole model
    """

    id = fields.IntField(pk=True)
    role = fields.ForeignKeyField(
        model_name="models.Role",
        on_delete=fields.RESTRICT,
        on_update=fields.CASCADE
    )
    product = fields.ForeignKeyField(
        model_name="models.Product",
        related_name="roles",
        on_delete=fields.CASCADE,
        on_update=fields.CASCADE
    )

    role_id: int
    product_id: int

    class Meta:
        table = "product_role"
        unique_together = ("role_id", "product_id")

    async def to_dict(self):
        return {
            "id": self.id,
            "role_id": self.role_id,
            "product_id": self.product_id,
        }
