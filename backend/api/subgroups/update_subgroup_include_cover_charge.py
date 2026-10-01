from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from backend.database.models import Subgroup
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import Conflict, NotFound
from backend.models.subgroups import (
    UpdateSubgroupIncludeCoverChargeItem,
)
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

update_subgroup_include_cover_charge_router = APIRouter()


@update_subgroup_include_cover_charge_router.put(
    "/{subgroup_id}/include_cover_charge", response_model=BaseResponse
)
@check_role(Permission.CAN_ADMINISTER)
async def update_subgroup_include_cover_charge(
    subgroup_id: int,
    item: UpdateSubgroupIncludeCoverChargeItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Update include_cover_charge of subgroup.

     **Permission**: can_administer
    """

    async with in_transaction() as connection:
        subgroup = await Subgroup.get_or_none(
            id=subgroup_id, using_db=connection
        )

        if not subgroup:
            raise NotFound(code=ErrorCodes.SUBGROUP_NOT_FOUND)

        subgroup.include_cover_charge = item.include_cover_charge

        try:
            await subgroup.save(using_db=connection)

        except IntegrityError:
            raise Conflict(code=ErrorCodes.SUBGROUP_ALREADY_EXISTS)

    return BaseResponse()
