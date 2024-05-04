from tortoise import fields
from tortoise.models import Model

from backend.utils import Category


class Product(Model):
    """
    The Product model
    """

    id = fields.IntField(pk=True)
    name = fields.CharField(32, unique=True)
    short_name = fields.CharField(20, unique=True)
    is_priority = fields.BooleanField(default=False)
    price = fields.FloatField()
    category = fields.CharEnumField(Category)
    subcategory = fields.ForeignKeyField(
        "models.Subcategory", related_name="subcategory_id"
    )

    class Meta:
        table = "product"

    async def to_dict_name(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "short_name": self.short_name,
        }

    async def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "short_name": self.short_name,
            "is_priority": self.is_priority,
            "price": self.price,
            "category": self.category,
            "subcategory_id": self.subcategory_id,
        }
