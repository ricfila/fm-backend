from fastapi import APIRouter, Depends
from tortoise.transactions import in_transaction

from backend.database.models import Product
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import NotFound
from backend.models.products import UpdateProductIsPriorityItem
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

update_product_is_priority_router = APIRouter()


@update_product_is_priority_router.put(
    "/{product_id}/priority", response_model=BaseResponse
)
@check_role(Permission.CAN_ADMINISTER)
async def update_product_is_priority(
    product_id: int,
    item: UpdateProductIsPriorityItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Update priority of product.

     **Permission**: can_administer
    """

    async with in_transaction() as connection:
        product = await Product.get_or_none(id=product_id, using_db=connection)

        if not product:
            raise NotFound(code=ErrorCodes.PRODUCT_NOT_FOUND)

        product.is_priority = item.is_priority

        await product.save(using_db=connection)

    return BaseResponse()
