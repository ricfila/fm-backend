from fastapi import APIRouter, Depends
from tortoise.exceptions import ParamsError
from tortoise.expressions import Q
from tortoise.transactions import in_transaction

from backend.database.models import Subgroup
from backend.decorators import check_role
from backend.models.error import BadRequest
from backend.models.subgroups import (
    GetSubgroupsResponse,
    Subgroup as SubgroupModel,
    SubgroupName,
)
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token
from backend.utils.query_utils import process_query_with_pagination

get_subgroups_router = APIRouter()

@get_subgroups_router.get("/", response_model=GetSubgroupsResponse)
@check_role(Permission.CAN_ADMINISTER, Permission.CAN_ORDER, Permission.CAN_CONFIRM_ORDERS)
async def get_subgroups(
    offset: int = 0,
    limit: int | None = None,
    only_name: bool = False,
    order_by: str = None,
    token: TokenJwt = Depends(validate_token),
):
    """
    Get list of subgroups.

    **Permission**: can_administer, can_order, can_confirm_orders
    """

    async with in_transaction() as connection:
        (
            subgroups_query,
            total_count,
            limit,
        ) = await process_query_with_pagination(
            Subgroup, Q(), connection, offset, limit, order_by
        )

        try:
            subgroups = await subgroups_query.offset(offset).limit(
                limit
            )
        except ParamsError:
            raise BadRequest(code=ErrorCodes.INVALID_OFFSET_OR_LIMIT_NEGATIVE)

    return GetSubgroupsResponse(
        total_count=total_count,
        subgroups=[
            SubgroupName(**await subgroup.to_dict_name())
            if only_name
            else SubgroupModel(**await subgroup.to_dict())
            for subgroup in subgroups
        ],
    )
