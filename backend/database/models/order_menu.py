import typing

from tortoise import fields
from tortoise.models import Model

if typing.TYPE_CHECKING:
    from backend.database.models import OrderMenuField


class OrderMenu(Model):
    """
    The OrderMenu model
    """

    id = fields.IntField(pk=True)
    menu = fields.ForeignKeyField("models.Menu")
    price = fields.FloatField()
    quantity = fields.IntField()
    order = fields.ForeignKeyField("models.Order", "order_menus")

    menu_id: int

    order_menu_fields: fields.ReverseRelation["OrderMenuField"]

    class Meta:
        table = "order_menu"

    async def to_dict(
        self,
        include_menu: bool = False,
        include_menu_dates: bool = False,
        include_menu_fields: bool = False,
        include_menu_fields_products: bool = False,
        include_menu_fields_products_dates: bool = False,
        include_menu_fields_products_ingredients: bool = False,
        include_menu_fields_products_roles: bool = False,
        include_menu_fields_products_variants: bool = False,
        include_menu_roles: bool = False,
        include_fields: bool = False,
        include_fields_products: bool = False,
        include_fields_products_ingredients: bool = False,
    ) -> dict:
        result = {
            "id": self.id,
            "menu_id": self.menu_id,
            "price": self.price,
            "quantity": self.quantity,
        }

        if include_menu:
            result["menu"] = await (await self.menu).to_dict(
                include_menu_dates,
                include_menu_fields,
                include_menu_fields_products,
                include_menu_fields_products_dates,
                include_menu_fields_products_ingredients,
                include_menu_fields_products_roles,
                include_menu_fields_products_variants,
                include_menu_roles,
            )

        if include_fields and hasattr(self, "order_menu_fields"):
            result["fields"] = [
                await field.to_dict(
                    include_fields_products,
                    include_fields_products_ingredients,
                )
                for field in self.order_menu_fields
            ]

        return result
