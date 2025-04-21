from tortoise import fields
from tortoise.models import Model


class Printer(Model):
    """
    The Printer model
    """

    id = fields.IntField(pk=True)
    name = fields.CharField(32, unique=True)
    ip_address = fields.CharField(15, unique=True)

    class Meta:
        table = "printer"

    async def to_dict_name(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
        }

    async def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "ip_address": self.ip_address,
        }
