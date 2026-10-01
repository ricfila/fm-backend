from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from backend.database.models import Subgroup
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import Conflict, NotFound
from backend.models.subgroups import UpdateSubgroupOrderItem
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

update_subgroup_order_router = APIRouter()


@update_subgroup_order_router.put(
    "/{subgroup_id}/order", response_model=BaseResponse
)
@check_role(Permission.CAN_ADMINISTER)
async def update_subgroup_order(
    subgroup_id: int,
    item: UpdateSubgroupOrderItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Update order of subgroup.

     **Permission**: can_administer
    """

    async with in_transaction() as connection:
        subgroup = await Subgroup.get_or_none(
            id=subgroup_id, using_db=connection
        )

        if not subgroup:
            raise NotFound(code=ErrorCodes.SUBGROUP_NOT_FOUND)

        subgroup.order = item.order

        try:
            await subgroup.save(using_db=connection)

        except IntegrityError:
            raise Conflict(code=ErrorCodes.SUBGROUP_ALREADY_EXISTS)

    return BaseResponse()
