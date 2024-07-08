from tortoise import fields
from tortoise.models import Model

from backend.database.utils import is_valid_date


class MenuDate(Model):
    """
    The MenuDate model
    """

    id = fields.IntField(pk=True)
    start_date = fields.DatetimeField()
    end_date = fields.DatetimeField()
    menu = fields.ForeignKeyField("models.Menu", "dates")

    menu_id: int

    class Meta:
        table = "menu_date"
        unique_together = ("start_date", "end_date", "menu_id")

    async def is_valid_menu_date(self) -> bool:
        return is_valid_date(self.start_date, self.end_date)

    async def check_date_overlaps(self):
        existing_records = await MenuDate.filter(menu_id=self.menu_id).all()

        for record in existing_records:
            if (self.start_date < record.end_date) and (
                self.end_date > record.start_date
            ):
                return True

        return False

    async def save(self, *args, **kwargs):
        if self.end_date < self.start_date:
            raise ValueError("End date must be greater than start date")

        if await self.check_date_overlaps():
            raise ValueError("Duplicate date")

        await super().save(*args, **kwargs)

    async def to_dict(self):
        return {
            "id": self.id,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "menu_id": self.menu_id,
        }
