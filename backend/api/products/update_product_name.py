from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError

from backend.database.models import Product
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import Conflict, NotFound
from backend.models.products import UpdateProductNameItem
from backend.utils import Permission, TokenJwt, validate_token

update_product_name_router = APIRouter()


@update_product_name_router.put(
    "/{product_id}/name", response_model=BaseResponse
)
@check_role(Permission.CAN_ADMINISTER)
async def update_product_name(
    product_id: int,
    item: UpdateProductNameItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Update name of product.

     **Permission**: can_administer
    """

    product = await Product.get_or_none(id=product_id)

    if not product:
        raise NotFound("Product not found")

    product.name = item.name

    try:
        await product.save()

    except IntegrityError:
        raise Conflict("Product already exists")

    return BaseResponse()
