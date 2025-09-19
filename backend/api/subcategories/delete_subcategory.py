from fastapi import APIRouter, Depends
from tortoise.transactions import in_transaction

from backend.database.models import Subcategory
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import NotFound
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

delete_subcategory_router = APIRouter()


@delete_subcategory_router.delete(
    "/{subcategory_id}", response_model=BaseResponse
)
@check_role(Permission.CAN_ADMINISTER)
async def delete_subcategory(
    subcategory_id: int, token: TokenJwt = Depends(validate_token)
):
    """
    Delete a subcategory from the id.

     **Permission**: can_administer
    """

    async with in_transaction() as connection:
        subcategory = await Subcategory.get_or_none(
            id=subcategory_id, using_db=connection
        )

        if not subcategory:
            raise NotFound(code=ErrorCodes.SUBCATEGORY_NOT_FOUND)

        await subcategory.delete(using_db=connection)

    return BaseResponse()
