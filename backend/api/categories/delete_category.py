from fastapi import APIRouter, Depends
from tortoise.exceptions import OperationalError
from tortoise.transactions import in_transaction

from backend.database.models import Category
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import Conflict, NotFound
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

delete_category_router = APIRouter()


@delete_category_router.delete("/{category_id}", response_model=BaseResponse)
@check_role(Permission.CAN_ADMINISTER)
async def delete_category(
    category_id: int,
    token: TokenJwt = Depends(validate_token)
):
    """
    Delete a category from the id.

     **Permission**: can_administer
    """

    async with in_transaction() as connection:
        category = await Category.get_or_none(
            id=category_id, using_db=connection
        )

        if not category:
            raise NotFound(code=ErrorCodes.CATEGORY_NOT_FOUND)

        try:
            await category.delete(using_db=connection)
        except OperationalError:
            raise Conflict(code=ErrorCodes.CATEGORY_IN_USE)

    return BaseResponse()
