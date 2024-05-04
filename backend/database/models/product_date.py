from tortoise import fields
from tortoise.models import Model


class ProductDate(Model):
    """
    The ProductDate model
    """

    id = fields.IntField(pk=True)
    start_date = fields.DatetimeField()
    end_date = fields.DatetimeField()
    product_id = fields.ForeignKeyField("models.Product")

    class Meta:
        table = "product_date"
        unique_together = ("start_date", "end_date", "product_id")

    async def to_dict(self):
        return {
            "id": self.id,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "product_id": self.product_id,
        }
