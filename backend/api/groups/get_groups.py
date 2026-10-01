from fastapi import APIRouter, Depends
from tortoise.exceptions import ParamsError
from tortoise.expressions import Q
from tortoise.transactions import in_transaction

from backend.database.models import Group
from backend.decorators import check_role
from backend.models.error import BadRequest
from backend.models.groups import (
    GetGroupsResponse,
    Group as GroupModel,
    GroupName,
)
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token
from backend.utils.query_utils import process_query_with_pagination

get_groups_router = APIRouter()

@get_groups_router.get("/", response_model=GetGroupsResponse)
@check_role(Permission.CAN_ADMINISTER, Permission.CAN_ORDER, Permission.CAN_CONFIRM_ORDERS)
async def get_groups(
    offset: int = 0,
    limit: int | None = None,
    order_by: str = None,
    token: TokenJwt = Depends(validate_token),
):
    """
    Get list of groups.

    **Permission**: can_administer, can_order, can_confirm_orders
    """

    async with in_transaction() as connection:
        (
            groups_query,
            total_count,
            limit,
        ) = await process_query_with_pagination(
            Group, Q(), connection, offset, limit, order_by
        )

        try:
            groups = await groups_query.offset(offset).limit(
                limit
            )
        except ParamsError:
            raise BadRequest(code=ErrorCodes.INVALID_OFFSET_OR_LIMIT_NEGATIVE)

    return GetGroupsResponse(
        total_count=total_count,
        groups=[GroupModel(**await group.to_dict()) for group in groups],
    )
