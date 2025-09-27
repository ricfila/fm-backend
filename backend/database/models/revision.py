from tortoise import fields
from tortoise.models import Model


class Revision(Model):
    """
    The Revision model
    """

    id = fields.IntField(pk=True)
    order = fields.ForeignKeyField(
        model_name="models.Order",
        related_name="order_revisions",
        on_delete=fields.CASCADE,
        on_update=fields.CASCADE
    )
    user = fields.ForeignKeyField(
        model_name="models.User",
        on_delete=fields.RESTRICT,
        on_update=fields.CASCADE
    )
    revised_at = fields.DatetimeField(auto_now_add=True)
    price_difference = fields.DecimalField(max_digits=10, decimal_places=2)
    edited_products = fields.IntField()

    order_id: int
    user_id: int

    class Meta:
        table = "revision"

    async def to_dict(self) -> dict:
        return {
            "id": self.id,
            "order_id": self.order_id,
            "user_id": self.user_id,
            "revised_at": self.revised_at,
            "price_difference": self.price_difference,
            "edited_products": self.edited_products
        }
