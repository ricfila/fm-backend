from fastapi import APIRouter, Depends

from backend.database.models import Menu
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import NotFound
from backend.utils import Permission, TokenJwt, validate_token

delete_menu_router = APIRouter()


@delete_menu_router.delete("/{menu_id}", response_model=BaseResponse)
@check_role(Permission.CAN_ADMINISTER)
async def delete_menu(menu_id: int, token: TokenJwt = Depends(validate_token)):
    """
    Delete a menu from the id.

    **Permission**: can_administer
    """

    menu = await Menu.get_or_none(id=menu_id)

    if not menu:
        raise NotFound("Menu not found")

    await menu.delete()

    return BaseResponse()
