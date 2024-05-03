from fastapi import APIRouter, Depends

from backend.database.models import Role
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import NotFound, Unauthorized
from backend.utils import Permission, TokenJwt, validate_token

delete_role_router = APIRouter()


@delete_role_router.delete("/{role_id}", response_model=BaseResponse)
@check_role(Permission.CAN_ADMINISTER)
async def delete_role(role_id: int, token: TokenJwt = Depends(validate_token)):
    """
    Delete a role from the id.

     **Permission**: can_administer
    """

    role = await Role.get_or_none(id=role_id)

    if not role:
        raise NotFound("Role not found")

    if role.name == "admin":
        raise Unauthorized("You do not have permission to delete this role")

    await role.delete()

    return BaseResponse()
