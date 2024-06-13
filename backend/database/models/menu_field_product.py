from tortoise import fields
from tortoise.models import Model


class MenuFieldProduct(Model):
    """
    The MenuFieldProduct model
    """

    id = fields.IntField(pk=True)
    price = fields.FloatField()
    product = fields.ForeignKeyField("models.Product")
    menu_field = fields.ForeignKeyField("models.MenuField", "fields_products")

    product_id: int
    menu_field_id: int

    class Meta:
        table = "menu_field_product"
        unique_together = ("product_id", "menu_field_id")

    async def to_dict(self):
        return {
            "id": self.id,
            "price": self.price,
            "product_id": self.product_id,
            "menu_field_id": self.menu_field_id,
        }
