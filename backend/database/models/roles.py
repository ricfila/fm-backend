from tortoise import fields
from tortoise.models import Model
from typing_extensions import override

from backend.utils import PaperSize


class Roles(Model):
    """
    The Roles model
    """

    id = fields.IntField(pk=True)
    name = fields.CharField(30, unique=True)
    administration = fields.BooleanField(default=False)
    can_order = fields.BooleanField(default=False)
    statistics = fields.BooleanField(default=False)
    priority_statistics = fields.BooleanField(default=False)
    paper_size = fields.CharEnumField(PaperSize, null=True)

    class Meta:
        table = "roles"

    @override
    async def save(self, *args, **kwargs):
        if self.statistics and self.priority_statistics:
            raise ValueError(
                "Only one of `statistics` and `priority_statistics` can be True."
            )

        await super().save(*args, **kwargs)
