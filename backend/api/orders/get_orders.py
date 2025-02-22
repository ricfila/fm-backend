from fastapi import APIRouter, Depends
from tortoise.exceptions import ParamsError
from tortoise.expressions import Q
from tortoise.transactions import in_transaction

from backend.database.models import Order
from backend.decorators import check_role
from backend.models.error import BadRequest, Unauthorized
from backend.models.orders import GetOrdersResponse, Order as OrderModel
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token
from backend.utils.query_utils import process_query_with_pagination

get_orders_router = APIRouter()


@get_orders_router.get("/", response_model=GetOrdersResponse)
@check_role(Permission.CAN_ADMINISTER)
async def get_orders(
    offset: int = 0,
    limit: int | None = None,
    order_by: str = None,
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
    token: TokenJwt = Depends(validate_token),
):
    """
    Get list of orders.

    **Permission**: can_administer
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
        orders_query, total_count, limit = await process_query_with_pagination(
            Order, Q(), connection, offset, limit, order_by
        )

        try:
            orders = (
                await orders_query.prefetch_related(
                    "order_menus__order_menu_fields__order_menu_field_products",
                    "order_products__order_product_ingredients",
                    "order_products__product__dates",
                    "order_products__product__ingredients",
                    "order_products__product__roles",
                    "order_products__product__variants",
                )
                .offset(offset)
                .limit(limit)
            )
        except ParamsError:
            raise BadRequest(code=ErrorCodes.INVALID_OFFSET_OR_LIMIT_NEGATIVE)

    return GetOrdersResponse(
        total_count=total_count,
        orders=[
            OrderModel(
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
                )
            )
            for order in orders
        ],
    )
