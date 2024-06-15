from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError

from backend.database.models import Menu
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import Conflict, NotFound
from backend.models.menu import UpdateMenuShortNameItem
from backend.utils import Permission, TokenJwt, validate_token

update_menu_short_name_router = APIRouter()


@update_menu_short_name_router.put(
    "/{menu_id}/short_name", response_model=BaseResponse
)
@check_role(Permission.CAN_ADMINISTER)
async def update_menu_short_name(
    menu_id: int,
    item: UpdateMenuShortNameItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Update short name of menu.

     **Permission**: can_administer
    """

    menu = await Menu.get_or_none(id=menu_id)

    if not menu:
        raise NotFound("Menu not found")

    menu.short_name = item.short_name

    try:
        await menu.save()

    except IntegrityError:
        raise Conflict("This short name already exists")

    return BaseResponse()
