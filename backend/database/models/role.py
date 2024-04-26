from tortoise import fields
from tortoise.models import Model

from backend.utils import PaperSize


class Role(Model):
    """
    The Role model
    """

    id = fields.IntField(pk=True)
    name = fields.CharField(32, unique=True)
    can_administer = fields.BooleanField(default=False)
    can_order = fields.BooleanField(default=False)
    can_statistics = fields.BooleanField(default=False)
    can_priority_statistics = fields.BooleanField(default=False)
    paper_size = fields.CharEnumField(PaperSize, null=True)

    class Meta:
        table = "role"

    async def save(self, *args, **kwargs):
        if self.can_statistics and self.can_priority_statistics:
            raise ValueError(
                "Only one of `can_statistics` and `can_priority_statistics` can be True"
            )

        if self.can_order and not self.paper_size:
            raise ValueError(
                "If `can_order` is `True` then `paper_size` is required"
            )

        await super().save(*args, **kwargs)

    async def get_permissions(self) -> dict:
        return {
            "can_administer": self.can_administer,
            "can_order": self.can_order,
            "can_statistics": self.can_statistics,
            "can_priority_statistics": self.can_priority_statistics,
        }

    async def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "permissions": await self.get_permissions(),
            "paper_size": self.paper_size,
        }
