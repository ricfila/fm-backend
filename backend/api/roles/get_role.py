from fastapi import APIRouter, Depends

from backend.database.models import Role
from backend.decorators import check_role
from backend.models.error import NotFound
from backend.models.roles import GetRoleResponse
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

get_role_router = APIRouter()


@get_role_router.get("/{role_id}", response_model=GetRoleResponse)
@check_role(Permission.CAN_ADMINISTER)
async def get_role(role_id: int, token: TokenJwt = Depends(validate_token)):
    """
    Get information about a role.

    **Permission**: can_administer
    """

    role = await Role.get_or_none(id=role_id)

    if not role:
        raise NotFound(code=ErrorCodes.ROLE_NOT_FOUND)

    return GetRoleResponse(
        id=role_id,
        name=role.name,
        permissions=await role.get_permissions(),
        paper_size=role.paper_size,
    )
