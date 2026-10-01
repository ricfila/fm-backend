from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from backend.database.models import Subgroup
from backend.decorators import check_role
from backend.models.error import Conflict
from backend.models.subgroups import (
    CreateSubgroupItem,
    CreateSubgroupResponse,
)
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

create_subgroup_router = APIRouter()


@create_subgroup_router.post("/", response_model=CreateSubgroupResponse)
@check_role(Permission.CAN_ADMINISTER)
async def create_subgroup(
    item: CreateSubgroupItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Create a new subgroup.

    **Permission**: can_administer
    """

    async with in_transaction() as connection:
        new_subgroup = Subgroup(name=item.name)

        try:
            await new_subgroup.save(using_db=connection)

        except IntegrityError:
            raise Conflict(code=ErrorCodes.SUBGROUP_ALREADY_EXISTS)

    return CreateSubgroupResponse(
        subgroup=await new_subgroup.to_dict()
    )
