from fastapi import APIRouter, Depends

from backend.database.models import Role
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import Conflict, NotFound, Unauthorized
from backend.models.roles import UpdateRolePermissionsItem
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

update_role_permissions_router = APIRouter()


@update_role_permissions_router.put(
    "/{role_id}/permissions", response_model=BaseResponse
)
@check_role(Permission.CAN_ADMINISTER)
async def update_role_permissions(
    role_id: int,
    item: UpdateRolePermissionsItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Update permissions of role.

    **Permission**: can_administer
    """

    role = await Role.get_or_none(id=role_id)

    if not role:
        raise NotFound(code=ErrorCodes.ROLE_NOT_FOUND)

    if role.name == "admin":
        raise Unauthorized(code=ErrorCodes.NOT_ALLOWED)

    for permission, value in item.permissions.items():
        setattr(role, permission, value)

    try:
        await role.save()

    except ValueError as e:
        raise Conflict(code=e.args[0])

    return BaseResponse()
