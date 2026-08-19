from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from backend.database.models import Menu
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import Conflict, NotFound
from backend.models.menu import UpdateMenuPrintNameItem
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

update_menu_print_name_router = APIRouter()


@update_menu_print_name_router.put(
    "/{menu_id}/print_name", response_model=BaseResponse
)
@check_role(Permission.CAN_ADMINISTER)
async def update_menu_print_name(
    menu_id: int,
    item: UpdateMenuPrintNameItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Update print name of menu.

     **Permission**: can_administer
    """

    async with in_transaction() as connection:
        menu = await Menu.get_or_none(id=menu_id, using_db=connection)

        if not menu:
            raise NotFound(code=ErrorCodes.MENU_NOT_FOUND)

        menu.print_name = item.print_name

        try:
            await menu.save(using_db=connection)

        except IntegrityError:
            raise Conflict(code=ErrorCodes.MENU_PRINT_NAME_ALREADY_EXISTS)

    return BaseResponse()
