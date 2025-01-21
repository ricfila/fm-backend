from fastapi import APIRouter, Depends
from tortoise.expressions import Q
from tortoise.transactions import in_transaction

from backend.database.models import Product
from backend.database.utils import get_current_time
from backend.models.error import NotFound, Unauthorized
from backend.models.products import GetProductResponse
from backend.utils import ErrorCodes, TokenJwt, validate_token

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
        query_filter = Q(id=product_id)
        current_time = get_current_time()

        if not token.permissions["can_administer"]:
            if include_dates or include_roles:
                raise Unauthorized(code=ErrorCodes.ADMIN_OPTION_REQUIRED)

            # Add a filter for the role
            query_filter &= Q(roles__role_id=token.role_id)

            # Add a filter for valid dates
            query_filter &= Q(
                dates__start_date__lt=current_time,
                dates__end_date__gt=current_time,
            )

        product = (
            await Product.filter(query_filter)
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
