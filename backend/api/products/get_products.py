from fastapi import APIRouter, Depends
from tortoise.exceptions import ParamsError
from tortoise.expressions import Q
from tortoise.transactions import in_transaction

from backend.database.models import Product
from backend.models.error import BadRequest
from backend.models.products import (
    GetProductsResponse,
    Product as ProductModel,
    ProductName,
)
from backend.utils import ErrorCodes, TokenJwt, validate_token
from backend.utils.query_filters import build_multiple_query_filter
from backend.utils.query_utils import process_query_with_pagination

get_products_router = APIRouter()


@get_products_router.get("/", response_model=GetProductsResponse)
async def get_products(
    offset: int = 0,
    limit: int | None = None,
    only_name: bool = False,
    order_by: str = None,
    subcategory_id: int = None,
    include_dates: bool = False,
    include_ingredients: bool = False,
    include_roles: bool = False,
    include_variants: bool = False,
    token: TokenJwt = Depends(validate_token),
):
    """
    Get list of products.
    """

    async with in_transaction() as connection:
        products_query_filter = build_multiple_query_filter(
            token, include_dates, include_roles
        )

        if subcategory_id:
            products_query_filter &= Q(subcategory_id=subcategory_id)

        (
            products_query,
            total_count,
            limit,
        ) = await process_query_with_pagination(
            Product, products_query_filter, connection, offset, limit, order_by
        )

        try:
            products = (
                await products_query.prefetch_related(
                    "dates", "ingredients", "roles", "variants"
                )
                .offset(offset)
                .limit(limit)
            )
        except ParamsError:
            raise BadRequest(code=ErrorCodes.INVALID_OFFSET_OR_LIMIT_NEGATIVE)

    return GetProductsResponse(
        total_count=total_count,
        products=[
            ProductName(**await product.to_dict_name())
            if only_name
            else ProductModel(
                **await product.to_dict(
                    include_dates,
                    include_ingredients,
                    include_roles,
                    include_variants,
                )
            )
            for product in products
        ],
    )
