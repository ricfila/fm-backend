from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from backend.database.models import Menu, MenuRole, Role
from backend.decorators import check_role
from backend.models.error import Conflict, NotFound, Unauthorized
from backend.models.menu import AddMenuRoleItem, AddMenuRoleResponse
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

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

    async with in_transaction() as connection:
        menu = await Menu.get_or_none(id=menu_id, using_db=connection)

        if not menu:
            raise NotFound(code=ErrorCodes.MENU_NOT_FOUND)

        role = await Role.get_or_none(id=item.role_id, using_db=connection)

        if not role:
            raise NotFound(code=ErrorCodes.ROLE_NOT_FOUND)

        if not role.can_order:
            raise Unauthorized(code=ErrorCodes.ROLE_CANNOT_ORDER)

        new_menu_role = MenuRole(role=role, menu=menu)

        try:
            await new_menu_role.save(using_db=connection)

        except IntegrityError:
            raise Conflict(code=ErrorCodes.MENU_ROLE_ALREADY_EXISTS)

    return AddMenuRoleResponse(role=await new_menu_role.to_dict())
