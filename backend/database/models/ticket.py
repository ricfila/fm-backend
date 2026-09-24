from tortoise import fields
from tortoise.models import Model


class Ticket(Model):
    """
    The Ticket model
    """

    id = fields.IntField(pk=True)
    order = fields.ForeignKeyField(
        to="models.Order",
        related_name="order_tickets",
        on_delete=fields.CASCADE
    )
    category = fields.ForeignKeyField(
        to="models.Category",
        related_name="ticket_category",
        on_delete=fields.RESTRICT
    )
    printed_at = fields.DatetimeField(null=True, db_default=None)
    completed_at = fields.DatetimeField(null=True, db_default=None)
    has_collapsed_categories = fields.BooleanField(db_default=False)

    order_id: int
    category_id: int

    class Meta:
        table = "ticket"

    async def to_dict(self) -> dict:
        return {
            "id": self.id,
            "order_id": self.order_id,
            "category_id": self.category_id,
            "printed_at": self.printed_at,
            "completed_at": self.completed_at,
            "has_collapsed_categories": self.has_collapsed_categories
        }

    async def to_dict_category(self) -> dict:
        category_name = await self.category.to_dict_name()
        return {
            "id": self.id,
            "category": category_name,
            "printed_at": self.printed_at,
            "completed_at": self.completed_at,
            "has_collapsed_categories": self.has_collapsed_categories
        }
