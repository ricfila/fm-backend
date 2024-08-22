from fastapi import APIRouter, Depends
from tortoise.transactions import in_transaction

from backend.database.models import Product
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import NotFound
from backend.models.products import UpdateProductPriceItem
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

update_product_price_router = APIRouter()


@update_product_price_router.put(
    "/{product_id}/price", response_model=BaseResponse
)
@check_role(Permission.CAN_ADMINISTER)
async def update_product_price(
    product_id: int,
    item: UpdateProductPriceItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Update price of product.

     **Permission**: can_administer
    """

    async with in_transaction() as connection:
        product = await Product.get_or_none(id=product_id, using_db=connection)

        if not product:
            raise NotFound(code=ErrorCodes.PRODUCT_NOT_FOUND)

        product.price = item.price

        await product.save(using_db=connection)

    return BaseResponse()
