import typing

from tortoise import fields
from tortoise.models import Model

if typing.TYPE_CHECKING:
    from backend.database.models import Product, Ticket


class Category(Model):
    """
    The Category model
    """

    id = fields.IntField(pk=True)
    name = fields.CharField(32, unique=True)
    print_delay = fields.IntField()
    wait_parent_category = fields.BooleanField(default=False)
    printer = fields.ForeignKeyField(
        to="models.Printer",
        related_name="category_printer",
        on_delete=fields.RESTRICT
    )
    parent_category = fields.ForeignKeyField(
        to="models.Category",
        related_name="children_category",
        on_delete=fields.RESTRICT,
        null=True
    )
    parent_for_take_away = fields.ForeignKeyField(
        to="models.Category",
        related_name="take_away_children",
        on_delete=fields.RESTRICT,
        null=True
    )
    parent_for_main_products = fields.ForeignKeyField(
        to="models.Category",
        related_name="main_products_children",
        on_delete=fields.RESTRICT,
        null=True
    )

    products = fields.ReverseRelation["Product"]
    tickets = fields.ReverseRelation["Ticket"]

    printer_id: int
    parent_category_id: int
    parent_for_take_away_id: int
    parent_for_main_products_id: int

    class Meta:
        table = "category"

    async def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "print_delay": self.print_delay,
            "wait_parent_category": self.wait_parent_category,
            "printer_id": self.printer_id,
            "parent_category_id": self.parent_category_id,
            "parent_for_take_away_id": self.parent_for_take_away_id,
            "parent_for_main_products_id": self.parent_for_main_products_id
        }

    async def to_dict_name(self) -> dict:
        return {
            "id": self.id,
            "name": self.name
        }
