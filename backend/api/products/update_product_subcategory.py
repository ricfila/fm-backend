from fastapi import APIRouter, Depends
from tortoise.transactions import in_transaction

from backend.database.models import Product, Subgroup
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import NotFound
from backend.models.products import UpdateProductSubgroupItem
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

update_product_subgroup_router = APIRouter()


@update_product_subgroup_router.put(
    "/{product_id}/subgroup", response_model=BaseResponse
)
@check_role(Permission.CAN_ADMINISTER)
async def update_product_subgroup(
    product_id: int,
    item: UpdateProductSubgroupItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Update subgroup of product.

     **Permission**: can_administer
    """

    async with in_transaction() as connection:
        product = await Product.get_or_none(id=product_id, using_db=connection)

        if not product:
            raise NotFound(code=ErrorCodes.PRODUCT_NOT_FOUND)

        subgroup = await Subgroup.get_or_none(
            id=item.subgroup_id, using_db=connection
        )

        if not subgroup:
            raise NotFound(code=ErrorCodes.SUBGROUP_NOT_FOUND)

        product.subgroup = subgroup

        await product.save(using_db=connection)

    return BaseResponse()
