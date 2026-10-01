from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from backend.database.models import Group
from backend.decorators import check_role
from backend.models.error import Conflict
from backend.models.groups import (
    CreateGroupItem,
    CreateGroupResponse,
)
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

create_group_router = APIRouter()


@create_group_router.post("/", response_model=CreateGroupResponse)
@check_role(Permission.CAN_ADMINISTER)
async def create_group(
    item: CreateGroupItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Create a new group.

    **Permission**: can_administer
    """

    async with in_transaction() as connection:
        new_group = Group(name=item.name)

        try:
            await new_group.save(using_db=connection)

        except IntegrityError:
            raise Conflict(code=ErrorCodes.GROUP_ALREADY_EXISTS)

    return CreateGroupResponse(
        group=await new_group.to_dict()
    )
