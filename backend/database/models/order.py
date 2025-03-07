import typing

from tortoise import fields
from tortoise.models import Model

if typing.TYPE_CHECKING:
    from backend.database.models import OrderMenu, OrderProduct


class Order(Model):
    """
    The Order model
    """

    id = fields.IntField(pk=True)
    customer = fields.CharField(32)
    guests = fields.IntField(null=True)
    is_take_away = fields.BooleanField()
    table = fields.IntField(null=True)
    user = fields.ForeignKeyField("models.User")
    created_at = fields.DatetimeField(auto_now_add=True)

    user_id: int

    order_menus: fields.ReverseRelation["OrderMenu"]
    order_products: fields.ReverseRelation["OrderProduct"]

    class Meta:
        table = "order"

    async def to_dict(
        self,
        include_menus: bool = False,
        include_menus_menu: bool = False,
        include_menus_menu_dates: bool = False,
        include_menus_menu_fields: bool = False,
        include_menus_menu_fields_products: bool = False,
        include_menus_menu_fields_products_dates: bool = False,
        include_menus_menu_fields_products_ingredients: bool = False,
        include_menus_menu_fields_products_roles: bool = False,
        include_menus_menu_fields_products_variants: bool = False,
        include_menus_menu_roles: bool = False,
        include_menus_fields: bool = False,
        include_menus_fields_products: bool = False,
        include_menus_fields_products_ingredients: bool = False,
        include_products: bool = False,
        include_products_product: bool = False,
        include_products_product_dates: bool = False,
        include_products_product_ingredients: bool = False,
        include_products_product_roles: bool = False,
        include_products_product_variants: bool = False,
        include_products_ingredients: bool = False,
        include_user: bool = False,
    ) -> dict:
        result = {
            "id": self.id,
            "customer": self.customer,
            "guests": self.guests,
            "is_take_away": self.is_take_away,
            "table": self.table,
            "created_at": self.created_at,
        }

        if include_menus and hasattr(self, "order_menus"):
            result["menus"] = [
                await menu.to_dict(
                    include_menus_menu,
                    include_menus_menu_dates,
                    include_menus_menu_fields,
                    include_menus_menu_fields_products,
                    include_menus_menu_fields_products_dates,
                    include_menus_menu_fields_products_ingredients,
                    include_menus_menu_fields_products_roles,
                    include_menus_menu_fields_products_variants,
                    include_menus_menu_roles,
                    include_menus_fields,
                    include_menus_fields_products,
                    include_menus_fields_products_ingredients,
                )
                for menu in self.order_menus
            ]

        if include_products and hasattr(self, "order_products"):
            result["products"] = [
                await product.to_dict(
                    include_products_product,
                    include_products_product_dates,
                    include_products_product_ingredients,
                    include_products_product_roles,
                    include_products_product_variants,
                    include_products_ingredients,
                )
                for product in self.order_products
                if not product.order_menu_field_id
            ]

        if include_user and hasattr(self, "user"):
            result["user"] = await self.user.to_dict()

        return result
