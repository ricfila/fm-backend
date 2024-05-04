from fastapi import APIRouter, Depends

from backend.database.models import Product
from backend.decorators import check_role
from backend.models.error import NotFound
from backend.models.products import GetProductResponse
from backend.utils import Permission, TokenJwt, validate_token

get_product_router = APIRouter()


@get_product_router.get("/{product_id}", response_model=GetProductResponse)
@check_role(Permission.CAN_ADMINISTER)
async def get_product(
    product_id: int, token: TokenJwt = Depends(validate_token)
):
    """
    Get information about a product.

    **Permission**: can_administer
    """

    product = await Product.get_or_none(id=product_id)

    if not product:
        raise NotFound("Product not found")

    return GetProductResponse(
        id=product_id,
        name=product.name,
        short_name=product.short_name,
        is_priority=product.is_priority,
        price=product.price,
        category=product.category,
        subcategory_id=product.subcategory_id,
    )
