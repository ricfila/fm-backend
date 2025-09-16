from fastapi import APIRouter, Depends
from tortoise.transactions import in_transaction

from backend.database.models import Order
from backend.decorators import check_role
from backend.models.error import Unauthorized, NotFound
from backend.models.orders import GetOrderResponse
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

get_order_router = APIRouter()


@get_order_router.get("/{order_id}", response_model=GetOrderResponse)
@check_role(
    Permission.CAN_ADMINISTER,
    Permission.CAN_ORDER,
    Permission.CAN_CONFIRM_ORDERS
)
async def get_order(
    order_id: int,
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
    include_payment_method: bool = False,
    include_user: bool = False,
    include_confirmer_user: bool = False,
    token: TokenJwt = Depends(validate_token),
):
    """
    Get information about an order.

    **Permission**: can_administer, can_order, can_confirm_orders
    """

    if not token.permissions["can_administer"]:
        if (
            include_menus_menu_dates
            or include_menus_menu_roles
            or include_menus_menu_fields_products_dates
            or include_menus_menu_fields_products_roles
            or include_products_product_dates
            or include_products_product_roles
        ):
            raise Unauthorized(code=ErrorCodes.ADMIN_OPTION_REQUIRED)

    async with in_transaction() as connection:
        order = (
            await Order.filter(id=order_id)
            .prefetch_related(
                "order_menus__order_menu_fields__order_menu_field_products",
                "order_menus__order_menu_fields__order_menu_field_products__order_product_ingredients",
                "order_menus__menu__dates",
                "order_menus__menu__menu_fields",
                "order_menus__menu__menu_fields__field_products",
                "order_menus__menu__menu_fields__field_products__product__dates",
                "order_menus__menu__menu_fields__field_products__product__ingredients",
                "order_menus__menu__menu_fields__field_products__product__roles",
                "order_menus__menu__menu_fields__field_products__product__variants",
                "order_menus__menu__roles",
                "order_products__order_product_ingredients",
                "order_products__product__dates",
                "order_products__product__ingredients",
                "order_products__product__roles",
                "order_products__product__variants",
                "payment_method",
                "user",
                "confirmed_by",
            )
            .using_db(connection)
            .first()
        )

        if not order:
            raise NotFound(code=ErrorCodes.ORDER_NOT_FOUND)

        if order.is_deleted:
            raise NotFound(code=ErrorCodes.ORDER_NOT_FOUND)

    return GetOrderResponse(
        **await order.to_dict(
            include_menus,
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
            include_products,
            include_products_product,
            include_products_product_dates,
            include_products_product_ingredients,
            include_products_product_roles,
            include_products_product_variants,
            include_products_ingredients,
            include_payment_method,
            include_user,
            include_confirmer_user,
        )
    )
