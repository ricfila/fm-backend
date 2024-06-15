from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError

from backend.database.models import Menu
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import Conflict, NotFound
from backend.models.menu import UpdateMenuNameItem
from backend.utils import Permission, TokenJwt, validate_token

update_menu_name_router = APIRouter()


@update_menu_name_router.put("/{menu_id}/name", response_model=BaseResponse)
@check_role(Permission.CAN_ADMINISTER)
async def update_menu_name(
    menu_id: int,
    item: UpdateMenuNameItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Update name of menu.

     **Permission**: can_administer
    """

    menu = await Menu.get_or_none(id=menu_id)

    if not menu:
        raise NotFound("Menu not found")

    menu.name = item.name

    try:
        await menu.save()

    except IntegrityError:
        raise Conflict("Menu already exists")

    return BaseResponse()
