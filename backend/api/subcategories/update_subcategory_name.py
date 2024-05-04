from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError

from backend.database.models import Subcategory
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import Conflict, NotFound
from backend.models.subcategories import UpdateSubcategoryNameItem
from backend.utils import Permission, TokenJwt, validate_token

update_subcategory_name_router = APIRouter()


@update_subcategory_name_router.put(
    "/{subcategory_id}/name", response_model=BaseResponse
)
@check_role(Permission.CAN_ADMINISTER)
async def update_subcategory_name(
    subcategory_id: int,
    item: UpdateSubcategoryNameItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Update name of subcategory.

     **Permission**: can_administer
    """

    subcategory = await Subcategory.get_or_none(id=subcategory_id)

    if not subcategory:
        raise NotFound("Subcategory not found")

    subcategory.name = item.name

    try:
        await subcategory.save()

    except IntegrityError:
        raise Conflict("Subcategory already exists")

    return BaseResponse()
