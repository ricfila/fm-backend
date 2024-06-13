import typing

from tortoise import fields
from tortoise.models import Model

if typing.TYPE_CHECKING:
    from backend.database.models import MenuDate, MenuField, MenuRole


class Menu(Model):
    """
    The Menu model
    """

    id = fields.IntField(pk=True)
    name = fields.CharField(32, unique=True)
    short_name = fields.CharField(20, unique=True)
    price = fields.FloatField()

    dates: fields.ReverseRelation["MenuDate"]
    menu_fields: fields.ReverseRelation["MenuField"]
    roles: fields.ReverseRelation["MenuRole"]

    class Meta:
        table = "menu"

    async def to_dict(
        self,
        include_dates: bool = False,
        include_fields: bool = False,
        include_roles: bool = False,
    ) -> dict:
        await self.fetch_related("dates", "menu_fields")

        result = {
            "id": self.id,
            "name": self.name,
            "short_name": self.short_name,
            "price": self.price,
        }

        if include_dates:
            result["dates"] = [await date.to_dict() for date in self.dates]

        if include_fields:
            result["fields"] = [
                await field.to_dict() for field in self.menu_fields
            ]

        if include_roles:
            result["roles"] = [await role.to_dict() for role in self.roles]

        return result
