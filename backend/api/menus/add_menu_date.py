from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError

from backend.database.models import Menu, MenuDate
from backend.decorators import check_role
from backend.models.error import Conflict, NotFound
from backend.models.menu import AddMenuDateItem, AddMenuDateResponse
from backend.utils import Permission, TokenJwt, validate_token

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

    menu = await Menu.get_or_none(id=menu_id)

    if not menu:
        raise NotFound("Menu not found")

    new_menu_date = MenuDate(
        start_date=item.start_date, end_date=item.end_date, menu=menu
    )

    try:
        await new_menu_date.save()

    except IntegrityError:
        raise Conflict("Menu date already exists")

    except ValueError as e:
        raise Conflict(e.args[0])

    return AddMenuDateResponse(date=await new_menu_date.to_dict())
