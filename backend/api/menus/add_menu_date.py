from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from backend.database.models import Menu, MenuDate
from backend.decorators import check_role
from backend.models.error import Conflict, NotFound
from backend.models.menu import AddMenuDateItem, AddMenuDateResponse
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

add_menu_date_router = APIRouter()


@add_menu_date_router.post(
    "/{menu_id}/date", response_model=AddMenuDateResponse
)
@check_role(Permission.CAN_ADMINISTER)
async def add_menu_date(
    menu_id: int,
    item: AddMenuDateItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Add menu date.

    **Permission**: can_administer
    """

    async with in_transaction() as connection:
        menu = await Menu.get_or_none(id=menu_id, using_db=connection)

        if not menu:
            raise NotFound(code=ErrorCodes.MENU_NOT_FOUND)

        new_menu_date = MenuDate(
            start_date=item.start_date, end_date=item.end_date, menu=menu
        )

        try:
            await new_menu_date.save(using_db=connection)

        except IntegrityError:
            raise Conflict(code=ErrorCodes.MENU_DATE_ALREADY_EXISTS)

        except ValueError as e:
            raise Conflict(code=e.args[0])

    return AddMenuDateResponse(date=await new_menu_date.to_dict())
