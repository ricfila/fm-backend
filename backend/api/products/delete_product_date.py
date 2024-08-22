from fastapi import APIRouter, Depends
from tortoise.transactions import in_transaction

from backend.database.models import Product, ProductDate
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import NotFound
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

delete_product_date_router = APIRouter()


@delete_product_date_router.delete(
    "/{product_id}/date/{product_date_id}", response_model=BaseResponse
)
@check_role(Permission.CAN_ADMINISTER)
async def delete_product_date(
    product_id: int,
    product_date_id: int,
    token: TokenJwt = Depends(validate_token),
):
    """
    Delete a product date from the id.

    **Permission**: can_administer
    """

    async with in_transaction() as connection:
        product = await Product.get_or_none(id=product_id, using_db=connection)

        if not product:
            raise NotFound(code=ErrorCodes.PRODUCT_NOT_FOUND)

        product_date = await ProductDate.get_or_none(
            id=product_date_id, product=product, using_db=connection
        )

        if not product_date:
            raise NotFound(code=ErrorCodes.PRODUCT_DATE_NOT_FOUND)

        await product_date.delete(using_db=connection)

    return BaseResponse()
