from fastapi import APIRouter, Depends
from tortoise.transactions import in_transaction

from backend.database.models import Menu
from backend.models.error import NotFound
from backend.models.menu import GetMenuResponse
from backend.utils import ErrorCodes, TokenJwt, validate_token
from backend.utils.query_filters import build_single_query_filter
from backend.utils.query_utils import get_orderable_entities

get_menu_router = APIRouter()


@get_menu_router.get("/{menu_id}", response_model=GetMenuResponse)
async def get_menu(
    menu_id: int,
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
    Get information about a menu.
    """

    async with in_transaction() as connection:
        query_filter = build_single_query_filter(
            menu_id,
            token,
            include_dates,
            include_roles,
            include_fields_products_dates,
            include_fields_products_roles,
        )

        (
            menu_annotation_expression,
            menu_query_filter,
        ) = await get_orderable_entities("order_menus", "quantity")

        if not token.permissions["can_administer"]:
            query_filter &= menu_query_filter

        menu = (
            await Menu.annotate(
                **(
                    menu_annotation_expression
                    if not token.permissions["can_administer"]
                    else {}
                )
            )
            .filter(query_filter)
            .prefetch_related(
                "dates",
                "menu_fields__field_products",
                "menu_fields__field_products__product__dates",
                "menu_fields__field_products__product__ingredients",
                "menu_fields__field_products__product__roles",
                "menu_fields__field_products__product__variants",
                "roles",
            )
            .using_db(connection)
            .first()
        )

        if not menu:
            raise NotFound(code=ErrorCodes.MENU_NOT_FOUND)

    return GetMenuResponse(
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
