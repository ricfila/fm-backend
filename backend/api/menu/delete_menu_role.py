from fastapi import APIRouter, Depends

from backend.database.models import Menu, MenuRole
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import NotFound
from backend.utils import Permission, TokenJwt, validate_token

delete_menu_role_router = APIRouter()


@delete_menu_role_router.delete(
    "/{menu_id}/role/{menu_role_id}", response_model=BaseResponse
)
@check_role(Permission.CAN_ADMINISTER)
async def delete_menu_role(
    menu_id: int,
    menu_role_id: int,
    token: TokenJwt = Depends(validate_token),
):
    """
    Delete a menu role from the id.

    **Permission**: can_administer
    """

    menu = await Menu.get_or_none(id=menu_id)

    if not menu:
        raise NotFound("Menu not found")

    menu_role = await MenuRole.get_or_none(id=menu_role_id, menu=menu)

    if not menu_role:
        raise NotFound("Menu role not found")

    await menu_role.delete()

    return BaseResponse()
