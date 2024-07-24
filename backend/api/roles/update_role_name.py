from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError

from backend.database.models import Role
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import Conflict, NotFound, Unauthorized
from backend.models.roles import UpdateRoleNameItem
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

update_role_name_router = APIRouter()


@update_role_name_router.put("/{role_id}/name", response_model=BaseResponse)
@check_role(Permission.CAN_ADMINISTER)
async def update_role_name(
    role_id: int,
    item: UpdateRoleNameItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Update name of role.

    **Permission**: can_administer
    """

    role = await Role.get_or_none(id=role_id)

    if not role:
        raise NotFound(code=ErrorCodes.ROLE_NOT_FOUND)

    if role.name == "admin":
        raise Unauthorized(code=ErrorCodes.NOT_ALLOWED)

    role.name = item.name

    try:
        await role.save()

    except IntegrityError:
        raise Conflict(code=ErrorCodes.ROLE_ALREADY_EXISTS)

    return BaseResponse()
