from fastapi import APIRouter, Depends
from tortoise.transactions import in_transaction

from backend.database.models import Subgroup
from backend.decorators import check_role
from backend.models.error import NotFound
from backend.models.subgroups import GetSubgroupResponse
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

get_subgroup_router = APIRouter()


@get_subgroup_router.get(
    "/{subgroup_id}", response_model=GetSubgroupResponse
)
@check_role(Permission.CAN_ADMINISTER, Permission.CAN_ORDER, Permission.CAN_CONFIRM_ORDERS)
async def get_subgroup(
    subgroup_id: int,
    token: TokenJwt = Depends(validate_token)
):
    """
    Get information about a subgroup.

    **Permission**: can_administer, can_order, can_confirm_orders
    """

    async with in_transaction() as connection:
        subgroup = await Subgroup.get_or_none(
            id=subgroup_id, using_db=connection
        )

        if not subgroup:
            raise NotFound(code=ErrorCodes.SUBGROUP_NOT_FOUND)

    return GetSubgroupResponse(
        id=subgroup_id,
        name=subgroup.name,
        order=subgroup.order,
        include_cover_charge=subgroup.include_cover_charge,
    )
