from fastapi import APIRouter, Depends

from backend.database.models import Product
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import NotFound
from backend.utils import Permission, TokenJwt, validate_token

delete_product_router = APIRouter()


@delete_product_router.delete("/{product_id}", response_model=BaseResponse)
@check_role(Permission.CAN_ADMINISTER)
async def delete_product(
    product_id: int, token: TokenJwt = Depends(validate_token)
):
    """
    Delete a product from the id.

    **Permission**: can_administer
    """

    product = await Product.get_or_none(id=product_id)

    if not product:
        raise NotFound("Product not found")

    await product.delete()

    return BaseResponse()
