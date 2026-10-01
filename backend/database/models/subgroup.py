from tortoise import fields
from tortoise.models import Model


class Subgroup(Model):
    """
    The Subgroup model
    """

    id = fields.IntField(pk=True)
    name = fields.CharField(32, unique=True)
    order = fields.IntField(db_default=0)
    include_cover_charge = fields.BooleanField(db_default=True)
    group = fields.ForeignKeyField(
        to="models.Group",
        on_delete=fields.RESTRICT
    )

    group_id: int

    class Meta:
        table = "subgroup"

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
            "group_id": self.group_id,
        }
