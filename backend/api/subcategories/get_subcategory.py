from fastapi import APIRouter, Depends
from tortoise.transactions import in_transaction

from backend.database.models import Subcategory
from backend.decorators import check_role
from backend.models.error import NotFound
from backend.models.subcategories import GetSubcategoryResponse
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

get_subcategory_router = APIRouter()


@get_subcategory_router.get(
    "/{subcategory_id}", response_model=GetSubcategoryResponse
)
@check_role(Permission.CAN_ADMINISTER, Permission.CAN_ORDER)
async def get_subcategory(
    subcategory_id: int,
    token: TokenJwt = Depends(validate_token)
):
    """
    Get information about a subcategory.

    **Permission**: can_administer, can_order
    """

    async with in_transaction() as connection:
        subcategory = await Subcategory.get_or_none(
            id=subcategory_id, using_db=connection
        )

        if not subcategory:
            raise NotFound(code=ErrorCodes.SUBCATEGORY_NOT_FOUND)

    return GetSubcategoryResponse(
        id=subcategory_id,
        name=subcategory.name,
        order=subcategory.order,
        include_cover_charge=subcategory.include_cover_charge,
    )
