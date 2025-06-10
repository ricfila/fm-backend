from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from backend.database.models import Subcategory
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import Conflict, NotFound
from backend.models.subcategories import (
    UpdateSubcategoryIncludeCoverChargeItem,
)
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

update_subcategory_include_cover_charge_router = APIRouter()


@update_subcategory_include_cover_charge_router.put(
    "/{subcategory_id}/include_cover_charge", response_model=BaseResponse
)
@check_role(Permission.CAN_ADMINISTER)
async def update_subcategory_include_cover_charge(
    subcategory_id: int,
    item: UpdateSubcategoryIncludeCoverChargeItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Update include_cover_charge of subcategory.

     **Permission**: can_administer
    """

    async with in_transaction() as connection:
        subcategory = await Subcategory.get_or_none(
            id=subcategory_id, using_db=connection
        )

        if not subcategory:
            raise NotFound(code=ErrorCodes.SUBCATEGORY_NOT_FOUND)

        subcategory.include_cover_charge = item.include_cover_charge

        try:
            await subcategory.save(using_db=connection)

        except IntegrityError:
            raise Conflict(code=ErrorCodes.SUBCATEGORY_ALREADY_EXISTS)

    return BaseResponse()
