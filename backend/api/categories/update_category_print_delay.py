from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from backend.database.models import Category
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import Conflict, NotFound
from backend.models.categories import UpdateCategoryPrintDelayItem
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

update_category_print_delay_router = APIRouter()


@update_category_print_delay_router.put("/{category_id}/print_delay", response_model=BaseResponse)
@check_role(Permission.CAN_ADMINISTER)
async def update_category_print_delay(
    category_id: int,
    item: UpdateCategoryPrintDelayItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Update the print_delay of a category.

     **Permission**: can_administer
    """

    async with in_transaction() as connection:
        category = await Category.get_or_none(id=category_id, using_db=connection)
        if not category:
            raise NotFound(code=ErrorCodes.CATEGORY_NOT_FOUND)

        category.print_delay = item.print_delay

        try:
            await category.save(using_db=connection)

        except IntegrityError:
            raise Conflict(code=ErrorCodes.CATEGORY_ALREADY_EXISTS)

    return BaseResponse()
