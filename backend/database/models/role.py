from tortoise import fields
from tortoise.models import Model

from backend.utils import PaperSize


class Role(Model):
    """
    The Role model
    """

    id = fields.IntField(pk=True)
    name = fields.CharField(30, unique=True)
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
                "Only one of `can_statistics` and `can_priority_statistics` can be True."
            )

        await super().save(*args, **kwargs)
