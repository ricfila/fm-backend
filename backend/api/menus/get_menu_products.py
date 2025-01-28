from fastapi import APIRouter, Depends
from tortoise.transactions import in_transaction

from backend.database.models import Menu
from backend.models.error import NotFound
from backend.models.menu import GetMenuProductsResponse
from backend.utils import ErrorCodes, TokenJwt, validate_token
from backend.utils.query_filters import build_single_query_filter

get_menu_products_router = APIRouter()


@get_menu_products_router.get(
    "/{menu_id}/products", response_model=GetMenuProductsResponse
)
async def get_menu_products(
    menu_id: int,
    include_ingredients: bool = False,
    include_variants: bool = False,
    token: TokenJwt = Depends(validate_token),
):
    """
    Get list of product in a menu.
    """

    async with in_transaction() as connection:
        # Build a query filter
        query_filter = build_single_query_filter(menu_id, token, False, False)

        # Fetch the menu with related products, ingredients, and variants
        menu = (
            await Menu.filter(query_filter)
            .prefetch_related(
                "menu_fields__field_products",
                "menu_fields__field_products__product__ingredients",
                "menu_fields__field_products__product__variants",
            )
            .using_db(connection)
            .first()
        )

        if not menu:
            raise NotFound(code=ErrorCodes.MENU_NOT_FOUND)

        # Get product details
        menu_products = [
            await field_product.product.to_dict(
                False, include_ingredients, False, include_variants
            )
            for field in menu.menu_fields
            for field_product in field.field_products
        ]

    return GetMenuProductsResponse(products=menu_products)
