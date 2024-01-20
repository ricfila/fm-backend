from fastapi import APIRouter, Depends

from backend.config import Session
from backend.database.models import Role
from backend.decorators import check_role
from backend.models.roles import GetRolesResponse
from backend.utils import Permission, TokenJwt, validate_token

get_roles_router = APIRouter()


@get_roles_router.get("/", response_model=GetRolesResponse)
@check_role(Permission.CAN_ADMINISTER)
async def get_roles(
    offset: int = 0,
    limit: int = Session.config.DEFAULT_LIMIT_VALUE,
    token: TokenJwt = Depends(validate_token),
):
    """
    Get list of roles.

    **Permission**: can_administer
    """

    roles = (
        await Role.exclude(id=token.role_id).all().offset(offset).limit(limit)
    )

    return GetRolesResponse(roles=[await role.to_dict() for role in roles])
