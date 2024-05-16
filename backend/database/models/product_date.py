import datetime
import pytz

from tortoise import fields
from tortoise.models import Model


class ProductDate(Model):
    """
    The ProductDate model
    """

    id = fields.IntField(pk=True)
    start_date = fields.DatetimeField()
    end_date = fields.DatetimeField()
    product = fields.ForeignKeyField("models.Product", "dates")

    product_id: int

    class Meta:
        table = "product_date"
        unique_together = ("start_date", "end_date", "product_id")

    async def is_valid_product_date(self) -> bool:
        current_time = datetime.datetime.now(pytz.UTC)

        if current_time < self.start_date or current_time > self.end_date:
            return False

        return True

    async def check_date_overlaps(self):
        existing_records = await ProductDate.filter(
            product_id=self.product_id
        ).all()

        for record in existing_records:
            if (self.start_date < record.end_date) and (
                self.end_date > record.start_date
            ):
                return True

        return False

    async def save(self, *args, **kwargs):
        if await self.check_date_overlaps():
            raise ValueError("Duplicate date")

        await super().save(*args, **kwargs)

    async def to_dict(self):
        return {
            "id": self.id,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "product_id": self.product_id,
        }
