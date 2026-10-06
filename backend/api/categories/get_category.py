from fastapi import APIRouter, Depends
from tortoise.transactions import in_transaction

from backend.database.models import Category
from backend.decorators import check_role
from backend.models.error import NotFound
from backend.models.categories import GetCategoryResponse
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

get_category_router = APIRouter()


@get_category_router.get("/{category_id}", response_model=GetCategoryResponse)
@check_role(Permission.CAN_ADMINISTER, Permission.CAN_CONFIRM_ORDERS)
async def get_category(
    category_id: int, token: TokenJwt = Depends(validate_token)
):
    """
    Get information about a category.

     **Permission**: can_administer, can_confirm_orders
    """

    async with in_transaction() as connection:
        category = await Category.get_or_none(id=category_id, using_db=connection)

        if not category:
            raise NotFound(code=ErrorCodes.CATEGORY_NOT_FOUND)

    return GetCategoryResponse(**await category.to_dict(), success=True)
