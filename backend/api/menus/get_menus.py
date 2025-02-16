from fastapi import APIRouter, Depends
from tortoise.exceptions import ParamsError
from tortoise.transactions import in_transaction

from backend.database.models import Menu
from backend.models.error import BadRequest
from backend.models.menu import GetMenusResponse, Menu as MenuModel
from backend.utils import ErrorCodes, TokenJwt, validate_token
from backend.utils.query_filters import build_multiple_query_filter
from backend.utils.query_utils import process_query_with_pagination

get_menus_router = APIRouter()


@get_menus_router.get("/", response_model=GetMenusResponse)
async def get_menus(
    offset: int = 0,
    limit: int | None = None,
    order_by: str = None,
    include_dates: bool = False,
    include_fields: bool = False,
    include_fields_products: bool = False,
    include_fields_products_dates: bool = False,
    include_fields_products_ingredients: bool = False,
    include_fields_products_roles: bool = False,
    include_fields_products_variants: bool = False,
    include_roles: bool = False,
    token: TokenJwt = Depends(validate_token),
):
    """
    Get list of menu.
    """

    async with in_transaction() as connection:
        menus_query_filter = build_multiple_query_filter(
            token,
            include_dates,
            include_roles,
            include_fields_products_dates,
            include_fields_products_roles,
        )

        menus_query, total_count, limit = await process_query_with_pagination(
            Menu, menus_query_filter, connection, offset, limit, order_by
        )

        try:
            menus = (
                await menus_query.prefetch_related(
                    "dates",
                    "menu_fields__field_products",
                    "menu_fields__field_products__product__dates",
                    "menu_fields__field_products__product__ingredients",
                    "menu_fields__field_products__product__roles",
                    "menu_fields__field_products__product__variants",
                    "roles",
                )
                .offset(offset)
                .limit(limit)
            )
        except ParamsError:
            raise BadRequest(code=ErrorCodes.INVALID_OFFSET_OR_LIMIT_NEGATIVE)

    return GetMenusResponse(
        total_count=total_count,
        menus=[
            MenuModel(
                **await menu.to_dict(
                    include_dates,
                    include_fields,
                    include_fields_products,
                    include_fields_products_dates,
                    include_fields_products_ingredients,
                    include_fields_products_roles,
                    include_fields_products_variants,
                    include_roles,
                )
            )
            for menu in menus
        ],
    )
