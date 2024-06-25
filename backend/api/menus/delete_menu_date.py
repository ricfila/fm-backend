from fastapi import APIRouter, Depends

from backend.database.models import Menu, MenuDate
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import NotFound
from backend.utils import Permission, TokenJwt, validate_token

delete_menu_date_router = APIRouter()


@delete_menu_date_router.delete(
    "/{menu_id}/date/{menu_date_id}", response_model=BaseResponse
)
@check_role(Permission.CAN_ADMINISTER)
async def delete_menu_date(
    menu_id: int,
    menu_date_id: int,
    token: TokenJwt = Depends(validate_token),
):
    """
    Delete a menu date from the id.

    **Permission**: can_administer
    """

    menu = await Menu.get_or_none(id=menu_id)

    if not menu:
        raise NotFound("Menu not found")

    menu_date = await MenuDate.get_or_none(id=menu_date_id, menu=menu)

    if not menu_date:
        raise NotFound("Menu date not found")

    await menu_date.delete()

    return BaseResponse()
