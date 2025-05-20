from fastapi import APIRouter, Depends
from tortoise.transactions import in_transaction

from backend.database.models import Product
from backend.models.error import NotFound
from backend.models.products import GetProductResponse
from backend.utils import ErrorCodes, TokenJwt, validate_token
from backend.utils.query_filters import build_single_query_filter
from backend.utils.query_utils import get_orderable_entities

get_product_router = APIRouter()


@get_product_router.get("/{product_id}", response_model=GetProductResponse)
async def get_product(
    product_id: int,
    include_dates: bool = False,
    include_ingredients: bool = False,
    include_roles: bool = False,
    include_variants: bool = False,
    token: TokenJwt = Depends(validate_token),
):
    """
    Get information about a product.
    """

    async with in_transaction() as connection:
        query_filter = build_single_query_filter(
            product_id, token, include_dates, include_roles
        )

        (
            product_annotation_expression,
            product_query_filter,
        ) = await get_orderable_entities("order_products", "quantity")

        if not token.permissions["can_administer"]:
            query_filter &= product_query_filter

        product = (
            await Product.annotate(
                **(
                    product_annotation_expression
                    if not token.permissions["can_administer"]
                    else {}
                )
            )
            .filter(query_filter)
            .prefetch_related("dates", "ingredients", "roles", "variants")
            .using_db(connection)
            .first()
        )

        if not product:
            raise NotFound(code=ErrorCodes.PRODUCT_NOT_FOUND)

    return GetProductResponse(
        **await product.to_dict(
            include_dates, include_ingredients, include_roles, include_variants
        )
    )
