from fastapi import APIRouter, Depends
from tortoise.transactions import in_transaction

from backend.database.models import Group
from backend.decorators import check_role
from backend.models.error import NotFound
from backend.models.groups import GetGroupResponse
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

get_group_router = APIRouter()


@get_group_router.get(
    "/{group_id}", response_model=GetGroupResponse
)
@check_role(Permission.CAN_ADMINISTER, Permission.CAN_ORDER, Permission.CAN_CONFIRM_ORDERS)
async def get_group(
    group_id: int,
    token: TokenJwt = Depends(validate_token)
):
    """
    Get information about a group.

    **Permission**: can_administer, can_order, can_confirm_orders
    """

    async with in_transaction() as connection:
        group = await Group.get_or_none(
            id=group_id, using_db=connection
        )

        if not group:
            raise NotFound(code=ErrorCodes.GROUP_NOT_FOUND)

    return GetGroupResponse(
        **await group.to_dict()
    )
