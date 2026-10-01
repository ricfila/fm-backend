from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from backend.database.models import Group, Subgroup
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import Conflict, NotFound
from backend.models.subgroups import UpdateSubgroupGroupItem
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

update_subgroup_group_router = APIRouter()


@update_subgroup_group_router.put(
    "/{subgroup_id}/group", response_model=BaseResponse
)
@check_role(Permission.CAN_ADMINISTER)
async def update_subgroup_group(
    subgroup_id: int,
    item: UpdateSubgroupGroupItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Update group of subgroup.

     **Permission**: can_administer
    """

    async with in_transaction() as connection:
        subgroup = await Subgroup.get_or_none(
            id=subgroup_id, using_db=connection
        )
        if not subgroup:
            raise NotFound(code=ErrorCodes.SUBGROUP_NOT_FOUND)
        
        group = await Group.get_or_none(
            id=item.group_id, using_db=connection
        )
        if not group:
            raise NotFound(code=ErrorCodes.GROUP_NOT_FOUND)

        subgroup.group = group

        try:
            await subgroup.save(using_db=connection)

        except IntegrityError:
            raise Conflict(code=ErrorCodes.SUBGROUP_ALREADY_EXISTS)

    return BaseResponse()
