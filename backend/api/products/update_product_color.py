from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from backend.database.models import Product
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import Conflict, NotFound
from backend.models.products import UpdateProductColorItem
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

update_product_color_router = APIRouter()


@update_product_color_router.put(
    "/{product_id}/color", response_model=BaseResponse
)
@check_role(Permission.CAN_ADMINISTER)
async def update_product_color(
    product_id: int,
    item: UpdateProductColorItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Update color of product.

     **Permission**: can_administer
    """

    async with in_transaction() as connection:
        product = await Product.get_or_none(id=product_id, using_db=connection)

        if not product:
            raise NotFound(code=ErrorCodes.PRODUCT_NOT_FOUND)

        product.color = item.color

        try:
            await product.save(using_db=connection)

        except IntegrityError:
            raise Conflict(code=ErrorCodes.PRODUCT_ALREADY_EXISTS)

    return BaseResponse()
