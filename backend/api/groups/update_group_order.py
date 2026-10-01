from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from backend.database.models import Group
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import Conflict, NotFound
from backend.models.groups import UpdateGroupOrderItem
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

update_group_order_router = APIRouter()


@update_group_order_router.put(
    "/{group_id}/order", response_model=BaseResponse
)
@check_role(Permission.CAN_ADMINISTER)
async def update_group_order(
    group_id: int,
    item: UpdateGroupOrderItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Update order of group.

     **Permission**: can_administer
    """

    async with in_transaction() as connection:
        group = await Group.get_or_none(
            id=group_id, using_db=connection
        )

        if not group:
            raise NotFound(code=ErrorCodes.GROUP_NOT_FOUND)

        group.order = item.order

        try:
            await group.save(using_db=connection)

        except IntegrityError:
            raise Conflict(code=ErrorCodes.GROUP_ALREADY_EXISTS)

    return BaseResponse()
