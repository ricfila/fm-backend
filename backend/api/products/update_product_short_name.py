from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError

from backend.database.models import Product
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import Conflict, NotFound
from backend.models.products import UpdateProductShortNameItem
from backend.utils import Permission, TokenJwt, validate_token

update_product_short_name_router = APIRouter()


@update_product_short_name_router.put(
    "/{product_id}/short_name", response_model=BaseResponse
)
@check_role(Permission.CAN_ADMINISTER)
async def update_product_short_name(
    product_id: int,
    item: UpdateProductShortNameItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Update short name of product.

     **Permission**: can_administer
    """

    product = await Product.get_or_none(id=product_id)

    if not product:
        raise NotFound("Product not found")

    product.short_name = item.short_name

    try:
        await product.save()

    except IntegrityError:
        raise Conflict("This short name already exists")

    return BaseResponse()
