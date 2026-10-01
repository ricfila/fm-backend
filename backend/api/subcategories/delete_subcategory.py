from fastapi import APIRouter, Depends
from tortoise.transactions import in_transaction

from backend.database.models import Subgroup
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import NotFound
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

delete_subgroup_router = APIRouter()


@delete_subgroup_router.delete(
    "/{subgroup_id}", response_model=BaseResponse
)
@check_role(Permission.CAN_ADMINISTER)
async def delete_subgroup(
    subgroup_id: int, token: TokenJwt = Depends(validate_token)
):
    """
    Delete a subgroup from the id.

     **Permission**: can_administer
    """

    async with in_transaction() as connection:
        subgroup = await Subgroup.get_or_none(
            id=subgroup_id, using_db=connection
        )

        if not subgroup:
            raise NotFound(code=ErrorCodes.SUBGROUP_NOT_FOUND)

        await subgroup.delete(using_db=connection)

    return BaseResponse()
