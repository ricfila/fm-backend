from tortoise import fields
from tortoise.models import Model


class Group(Model):
    """
    The Group model
    """

    id = fields.IntField(pk=True)
    name = fields.CharField(32, unique=True)
    order = fields.IntField(db_default=0)

    class Meta:
        table = "group"

    async def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "order": self.order,
        }
