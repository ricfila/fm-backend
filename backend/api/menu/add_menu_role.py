from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError

from backend.database.models import Menu, MenuRole, Role
from backend.decorators import check_role
from backend.models.error import Conflict, NotFound, Unauthorized
from backend.models.menu import AddMenuRoleItem, AddMenuRoleResponse
from backend.utils import Permission, TokenJwt, validate_token

add_menu_role_router = APIRouter()


@add_menu_role_router.post(
    "/{menu_id}/role", response_model=AddMenuRoleResponse
)
@check_role(Permission.CAN_ADMINISTER)
async def add_menu_role(
    menu_id: int,
    item: AddMenuRoleItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Add menu role.

    **Permission**: can_administer
    """

    menu = await Menu.get_or_none(id=menu_id)

    if not menu:
        raise NotFound("Menu not found")

    role = await Role.get_or_none(id=item.role_id)

    if not role:
        raise NotFound("Role not found")

    if not role.can_order:
        raise Unauthorized("The role can not order")

    new_menu_role = MenuRole(role=role, menu=menu)

    try:
        await new_menu_role.save()

    except IntegrityError:
        raise Conflict("Menu role already exists")

    return AddMenuRoleResponse(role=await new_menu_role.to_dict())
