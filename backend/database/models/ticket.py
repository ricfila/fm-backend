from tortoise import fields
from tortoise.models import Model


class Ticket(Model):
    """
    The Ticket model
    """

    id = fields.IntField(pk=True)
    order = fields.ForeignKeyField(
        model_name="models.Order",
        related_name="order_tickets",
        on_delete=fields.CASCADE,
        on_update=fields.CASCADE
    )
    category = fields.ForeignKeyField(
        model_name="models.Category",
        related_name="ticket_category",
        on_delete=fields.RESTRICT,
        on_update=fields.CASCADE
    )
    printed_at = fields.BooleanField(null=True, default=None)

    order_id: int
    category_id: int

    class Meta:
        table = "ticket"

    async def to_dict(self) -> dict:
        return {
            "id": self.id,
            "order_id": self.order_id,
            "category_id": self.category_id,
            "printed_at": self.printed_at
        }

    async def to_dict_category(self) -> dict:
        category_name = await self.category.to_dict_name()
        return {
            "id": self.id,
            "category": category_name,
            "printed_at": self.printed_at
        }
