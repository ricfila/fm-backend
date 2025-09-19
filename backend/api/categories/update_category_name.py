from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from backend.database.models import Category
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import Conflict, NotFound
from backend.models.categories import UpdateCategoryNameItem
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

update_category_name_router = APIRouter()


@update_category_name_router.put("/{category_id}/name", response_model=BaseResponse)
@check_role(Permission.CAN_ADMINISTER)
async def update_category_name(
    category_id: int,
    item: UpdateCategoryNameItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Update the name of a category.

     **Permission**: can_administer
    """

    async with in_transaction() as connection:
        category = await Category.get_or_none(id=category_id, using_db=connection)
        if not category:
            raise NotFound(code=ErrorCodes.CATEGORY_NOT_FOUND)

        category.name = item.name

        try:
            await category.save(using_db=connection)

        except IntegrityError:
            raise Conflict(code=ErrorCodes.CATEGORY_ALREADY_EXISTS)

    return BaseResponse()
