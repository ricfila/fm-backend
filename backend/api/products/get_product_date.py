from fastapi import APIRouter, Depends

from backend.database.models import Product, ProductRole, ProductDate
from backend.models.error import NotFound, Unauthorized
from backend.models.products import GetProductDatesResponse
from backend.utils import TokenJwt, validate_token

get_product_date_router = APIRouter()


@get_product_date_router.get(
    "/{product_id}/date", response_model=GetProductDatesResponse
)
async def get_product_date(
    product_id: int, token: TokenJwt = Depends(validate_token)
):
    """
    Get information about a product date.
    """

    product = await Product.get_or_none(id=product_id)

    if not product:
        raise NotFound("Product not found")

    if not token.permissions["can_administer"]:
        product_role = await ProductRole.get_or_none(
            product=product, role_id=token.role_id
        )

        if not product_role:
            raise Unauthorized(
                "You do not have permission to get this product"
            )

    product_dates = await ProductDate.filter(product=product)

    return GetProductDatesResponse(
        product_dates=[
            await product_date.to_dict() for product_date in product_dates
        ]
    )
