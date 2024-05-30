from fastapi import APIRouter, Depends

from backend.database.models import Product, Subcategory
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import NotFound
from backend.models.products import UpdateProductSubcategoryItem
from backend.utils import Permission, TokenJwt, validate_token

update_product_subcategory_router = APIRouter()


@update_product_subcategory_router.put(
    "/{product_id}/subcategory", response_model=BaseResponse
)
@check_role(Permission.CAN_ADMINISTER)
async def update_product_subcategory(
    product_id: int,
    item: UpdateProductSubcategoryItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Update subcategory of product.

     **Permission**: can_administer
    """

    product = await Product.get_or_none(id=product_id)

    if not product:
        raise NotFound("Product not found")

    subcategory = Subcategory.get_or_none(id=item.subcategory_id)

    if not subcategory:
        raise NotFound("Subcategory not found")

    product.subcategory = subcategory

    await product.save()

    return BaseResponse()
