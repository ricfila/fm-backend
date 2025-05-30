from fastapi import APIRouter, Depends
from tortoise.query_utils import Prefetch
from tortoise.transactions import in_transaction

from backend.database.models import Menu, ProductIngredient, ProductVariant
from backend.models.error import NotFound
from backend.models.menu import GetMenuProductsResponse
from backend.utils import ErrorCodes, TokenJwt, validate_token
from backend.utils.query_filters import build_single_query_filter
from backend.utils.query_utils import get_orderable_entities

get_menu_products_router = APIRouter()


@get_menu_products_router.get(
    "/{menu_id}/products", response_model=GetMenuProductsResponse
)
async def get_menu_products(
    menu_id: int,
    include_dates: bool = False,
    include_ingredients: bool = False,
    include_roles: bool = False,
    include_variants: bool = False,
    token: TokenJwt = Depends(validate_token),
):
    """
    Get list of product in a menu.
    """

    async with in_transaction() as connection:
        # Build a query filter
        query_filter = build_single_query_filter(
            menu_id, token, include_dates, include_roles
        )

        (
            menu_annotation_expression,
            menu_query_filter,
        ) = await get_orderable_entities("order_menus", "quantity")

        if not token.permissions["can_administer"]:
            query_filter &= menu_query_filter

        # Fetch the menu with related products, ingredients, and variants
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
                "menu_fields__field_products",
                "menu_fields__field_products__product__dates",
                "menu_fields__field_products__product__roles",
                Prefetch(
                    "menu_fields__field_products__product__ingredients",
                    queryset=ProductIngredient.filter(is_deleted=False),
                ),
                Prefetch(
                    "menu_fields__field_products__product__variants",
                    queryset=ProductVariant.filter(is_deleted=False),
                ),
            )
            .using_db(connection)
            .first()
        )

        if not menu:
            raise NotFound(code=ErrorCodes.MENU_NOT_FOUND)

        # Get product details
        menu_products = [
            await field_product.product.to_dict(
                include_dates,
                include_ingredients,
                include_roles,
                include_variants,
            )
            for field in menu.menu_fields
            for field_product in field.field_products
        ]

    return GetMenuProductsResponse(products=menu_products)
