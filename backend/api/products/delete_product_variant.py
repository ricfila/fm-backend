from fastapi import APIRouter, Depends
from tortoise.transactions import in_transaction

from backend.database.models import Product, ProductVariant
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import NotFound
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

delete_product_variant_router = APIRouter()


@delete_product_variant_router.delete(
    "/{product_id}/variant/{product_variant_id}", response_model=BaseResponse
)
@check_role(Permission.CAN_ADMINISTER)
async def delete_product_variant(
    product_id: int,
    product_variant_id: int,
    token: TokenJwt = Depends(validate_token),
):
    """
    Delete a product variant from the id.

    **Permission**: can_administer
    """

    async with in_transaction() as connection:
        product = await Product.get_or_none(id=product_id, using_db=connection)

        if not product:
            raise NotFound(code=ErrorCodes.PRODUCT_NOT_FOUND)

        product_variant = await ProductVariant.get_or_none(
            id=product_variant_id, product=product, using_db=connection
        )

        if not product_variant:
            raise NotFound(code=ErrorCodes.PRODUCT_VARIANT_NOT_FOUND)

        product_variant.is_deleted = True
        await product_variant.save(using_db=connection)

    return BaseResponse()
