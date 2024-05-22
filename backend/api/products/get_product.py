from fastapi import APIRouter, Depends

from backend.database.models import Product
from backend.models.error import NotFound, Unauthorized
from backend.models.products import (
    GetProductResponse,
    GetProductAdministratorResponse,
)
from backend.utils import TokenJwt, validate_token

get_product_router = APIRouter()


@get_product_router.get(
    "/{product_id}", response_model=GetProductAdministratorResponse
)
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

    product = await Product.get_or_none(id=product_id).prefetch_related(
        "dates", "roles"
    )

    if not product:
        raise NotFound("Product not found")

    if not token.permissions["can_administer"]:
        if include_dates or include_roles:
            raise Unauthorized(
                "Only an administrator can use `include_dates` or `include_roles` option"
            )

        if not any([role.role_id == token.role_id for role in product.roles]):
            raise Unauthorized(
                "You do not have permission to get this product"
            )

        if not any(
            [await date.is_valid_product_date() for date in product.dates]
        ):
            raise Unauthorized(
                "You do not have permission to get this product"
            )

    return (
        GetProductAdministratorResponse
        if token.permissions["can_administer"]
        else GetProductResponse
    )(
        **await product.to_dict(
            include_dates, include_ingredients, include_roles, include_variants
        )
    )
