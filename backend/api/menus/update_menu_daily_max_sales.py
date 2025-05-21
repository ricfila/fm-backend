from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from backend.database.models import Menu
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import Conflict, NotFound
from backend.models.menu import UpdateMenuDailyMaxSales
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

update_menu_daily_max_sales_router = APIRouter()


@update_menu_daily_max_sales_router.put(
    "/{menu_id}/daily_max_sales", response_model=BaseResponse
)
@check_role(Permission.CAN_ADMINISTER)
async def update_menu_daily_max_sales(
    menu_id: int,
    item: UpdateMenuDailyMaxSales,
    token: TokenJwt = Depends(validate_token),
):
    """
    Update daily max sales of menu.

     **Permission**: can_administer
    """

    async with in_transaction() as connection:
        menu = await Menu.get_or_none(id=menu_id, using_db=connection)

        if not menu:
            raise NotFound(code=ErrorCodes.MENU_NOT_FOUND)

        menu.daily_max_sales = item.daily_max_sales

        try:
            await menu.save(using_db=connection)

        except IntegrityError:
            raise Conflict(code=ErrorCodes.MENU_ALREADY_EXISTS)

    return BaseResponse()
