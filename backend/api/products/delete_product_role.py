from fastapi import APIRouter, Depends
from tortoise.transactions import in_transaction

from backend.database.models import Product, ProductRole
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import NotFound
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

delete_product_role_router = APIRouter()


@delete_product_role_router.delete(
    "/{product_id}/role/{product_role_id}", response_model=BaseResponse
)
@check_role(Permission.CAN_ADMINISTER)
async def delete_product_role(
    product_id: int,
    product_role_id: int,
    token: TokenJwt = Depends(validate_token),
):
    """
    Delete a product role from the id.

    **Permission**: can_administer
    """

    async with in_transaction() as connection:
        product = await Product.get_or_none(id=product_id, using_db=connection)

        if not product:
            raise NotFound(code=ErrorCodes.PRODUCT_NOT_FOUND)

        product_role = await ProductRole.get_or_none(
            id=product_role_id, product=product, using_db=connection
        )

        if not product_role:
            raise NotFound(code=ErrorCodes.PRODUCT_ROLE_NOT_FOUND)

        await product_role.delete(using_db=connection)

    return BaseResponse()
