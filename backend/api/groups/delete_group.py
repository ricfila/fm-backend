from fastapi import APIRouter, Depends
from tortoise.transactions import in_transaction

from backend.database.models import Group
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import NotFound
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

delete_group_router = APIRouter()


@delete_group_router.delete(
    "/{group_id}", response_model=BaseResponse
)
@check_role(Permission.CAN_ADMINISTER)
async def delete_group(
    group_id: int, token: TokenJwt = Depends(validate_token)
):
    """
    Delete a group from the id.

     **Permission**: can_administer
    """

    async with in_transaction() as connection:
        group = await Group.get_or_none(
            id=group_id, using_db=connection
        )

        if not group:
            raise NotFound(code=ErrorCodes.GROUP_NOT_FOUND)

        await group.delete(using_db=connection)

    return BaseResponse()
