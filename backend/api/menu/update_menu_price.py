from fastapi import APIRouter, Depends

from backend.database.models import Menu
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import NotFound
from backend.models.menu import UpdateMenuPriceItem
from backend.utils import Permission, TokenJwt, validate_token

update_menu_price_router = APIRouter()


@update_menu_price_router.put("/{menu_id}/price", response_model=BaseResponse)
@check_role(Permission.CAN_ADMINISTER)
async def update_menu_price(
    menu_id: int,
    item: UpdateMenuPriceItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Update price of menu.

     **Permission**: can_administer
    """

    menu = await Menu.get_or_none(id=menu_id)

    if not menu:
        raise NotFound("Menu not found")

    menu.price = item.price

    await menu.save()

    return BaseResponse()
