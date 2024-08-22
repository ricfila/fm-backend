from fastapi import APIRouter, Depends
from tortoise.transactions import in_transaction

from backend.database.models import Product
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
        product = await Product.get_or_none(
            id=product_id, using_db=connection
        ).prefetch_related("dates", "roles")

        if not product:
            raise NotFound(code=ErrorCodes.PRODUCT_NOT_FOUND)

        if not token.permissions["can_administer"]:
            if include_dates or include_roles:
                raise Unauthorized(code=ErrorCodes.ADMIN_OPTION_REQUIRED)

            if not any(
                [role.role_id == token.role_id for role in product.roles]
            ):
                raise Unauthorized(code=ErrorCodes.NOT_ALLOWED)

            if not any(
                [await date.is_valid_product_date() for date in product.dates]
            ):
                raise Unauthorized(code=ErrorCodes.NOT_ALLOWED)

    return GetProductResponse(
        **await product.to_dict(
            include_dates, include_ingredients, include_roles, include_variants
        )
    )
