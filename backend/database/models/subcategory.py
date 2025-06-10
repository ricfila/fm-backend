from tortoise import fields
from tortoise.models import Model


class Subcategory(Model):
    """
    The Subcategory model
    """

    id = fields.IntField(pk=True)
    name = fields.CharField(32, unique=True)
    order = fields.IntField(default=0)
    include_cover_charge = fields.BooleanField(default=False)

    class Meta:
        table = "subcategory"

    async def to_dict_name(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "include_cover_charge": self.include_cover_charge,
        }

    async def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "order": self.order,
            "include_cover_charge": self.include_cover_charge,
        }
