from fastapi import APIRouter, Depends

from backend.database.models import Role
from backend.decorators import check_role
from backend.models.error import NotFound
from backend.models.roles import GetRoleResponse
from backend.utils import Permission, TokenJwt, validate_token

get_role_router = APIRouter()


@get_role_router.get("/{id}", response_model=GetRoleResponse)
@check_role(Permission.CAN_ADMINISTER)
async def get_role(id: int, token: TokenJwt = Depends(validate_token)):
    """
    Get information about a role.

     **Permission**: can_administer
    """

    role = await Role.get_or_none(id=id)

    if not role:
        raise NotFound("Role not found")

    return GetRoleResponse(
        id=id,
        name=role.name,
        permissions=await role.get_permissions(),
        paper_size=role.paper_size,
    )
