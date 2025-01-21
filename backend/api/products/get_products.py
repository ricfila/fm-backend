from fastapi import APIRouter, Depends
from tortoise.exceptions import FieldError, ParamsError
from tortoise.expressions import Q
from tortoise.transactions import in_transaction

from backend.database.models import Product
from backend.database.utils import get_current_time
from backend.models.error import NotFound, Unauthorized, BadRequest
from backend.models.products import (
    GetProductsResponse,
    Product as ProductModel,
    ProductName,
)
from backend.utils import ErrorCodes, TokenJwt, validate_token

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
        products_query_filter = Q()
        current_time = get_current_time()

        if subcategory_id:
            products_query_filter &= Q(subcategory_id=subcategory_id)

        if not token.permissions["can_administer"]:
            if include_dates or include_roles:
                raise Unauthorized(code=ErrorCodes.ADMIN_OPTION_REQUIRED)

            # Add a filter for the role
            products_query_filter &= Q(roles__role_id=token.role_id)

            # Add a filter for valid dates
            products_query_filter &= Q(
                dates__start_date__lt=current_time,
                dates__end_date__gt=current_time,
            )

        products_query = Product.filter(products_query_filter).using_db(
            connection
        )

        total_count = await products_query.count()

        if not limit:
            limit = total_count - offset

        if order_by:
            try:
                products_query = products_query.order_by(order_by)
            except FieldError:
                raise NotFound(code=ErrorCodes.UNKNOWN_ORDER_BY_PARAMETER)

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
