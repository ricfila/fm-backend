from tortoise import fields
from tortoise.models import Model

from backend.database.utils import is_valid_date
from backend.utils import ErrorCodes


class ProductDate(Model):
    """
    The ProductDate model
    """

    id = fields.IntField(pk=True)
    start_date = fields.DatetimeField()
    end_date = fields.DatetimeField()
    product = fields.ForeignKeyField(
        model_name="models.Product",
        related_name="dates",
        on_delete=fields.CASCADE,
        on_update=fields.CASCADE
    )

    product_id: int

    class Meta:
        table = "product_date"
        unique_together = ("start_date", "end_date", "product_id")

    async def is_valid_product_date(self) -> bool:
        return is_valid_date(self.start_date, self.end_date)

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
        if self.end_date < self.start_date:
            raise ValueError(ErrorCodes.DATE_RANGE_INVALID)

        if await self.check_date_overlaps():
            raise ValueError(ErrorCodes.DUPLICATE_DATE)

        await super().save(*args, **kwargs)

    async def to_dict(self):
        return {
            "id": self.id,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "product_id": self.product_id,
        }
