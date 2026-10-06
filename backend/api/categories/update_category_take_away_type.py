from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from backend.database.models import Category
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import Conflict, NotFound
from backend.models.categories import UpdateTakeAwayTypeItem
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

update_category_take_away_type_router = APIRouter()


@update_category_take_away_type_router.put("/{category_id}/take_away_type", response_model=BaseResponse)
@check_role(Permission.CAN_ADMINISTER)
async def update_category_take_away_type(
    category_id: int,
    item: UpdateTakeAwayTypeItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Update the take away type of a category.

     **Permission**: can_administer
    """

    async with in_transaction() as connection:
        category = await Category.get_or_none(id=category_id, using_db=connection)
        if not category:
            raise NotFound(code=ErrorCodes.CATEGORY_NOT_FOUND)

        if (
            item.take_away_type is not None and
            category.parent_category is not None or category.parent_for_main_products is not None
        ):
            raise Conflict(code=ErrorCodes.TAKE_AWAY_CATEGORY_CANNOT_HAVE_PARENT)

        take_away_category = await Category.get_or_none(take_away_type=item.take_away_type, using_db=connection)
        if take_away_category and take_away_category.id != category_id:
            raise Conflict(code=ErrorCodes.TAKE_AWAY_CATEGORY_ALREADY_EXISTS)
        
        category.take_away_type = item.take_away_type

        try:
            await category.save(using_db=connection)

        except IntegrityError:
            raise Conflict(code=ErrorCodes.CATEGORY_ALREADY_EXISTS)

    return BaseResponse()
