from tortoise import fields
from tortoise.models import Model


class Ticket(Model):
    """
    The Ticket model
    """

    id = fields.IntField(pk=True)
    order = fields.ForeignKeyField("models.Order")
    category = fields.ForeignKeyField("models.Category")
    is_printed = fields.BooleanField(default=False)

    order_id: int
    category_id: int

    class Meta:
        table = "ticket"

    async def to_dict(self) -> dict:
        return {
            "id": self.id,
            "order_id": self.order_id,
            "category_id": self.category_id,
            "is_printed": self.is_printed
        }

    async def to_dict_category(self) -> dict:
        category = await self.category
        category_name = await category.to_dict_name()
        return {
            "id": self.id,
            "category": category_name,
            "is_printed": self.is_printed
        }
