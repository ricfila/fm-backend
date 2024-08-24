from fastapi import APIRouter, Depends
from tortoise.transactions import in_transaction

from backend.database.models import Menu
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import NotFound
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

delete_menu_router = APIRouter()


@delete_menu_router.delete("/{menu_id}", response_model=BaseResponse)
@check_role(Permission.CAN_ADMINISTER)
async def delete_menu(menu_id: int, token: TokenJwt = Depends(validate_token)):
    """
    Delete a menu from the id.

    **Permission**: can_administer
    """

    async with in_transaction() as connection:
        menu = await Menu.get_or_none(id=menu_id, using_db=connection)

        if not menu:
            raise NotFound(code=ErrorCodes.MENU_NOT_FOUND)

        await menu.delete(using_db=connection)

    return BaseResponse()
