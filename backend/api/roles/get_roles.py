from fastapi import APIRouter, Depends

from backend.config import Session
from backend.database.models import Role
from backend.decorators import check_role
from backend.models.roles import GetRolesResponse, Role as RoleModel, RoleName
from backend.utils import Permission, TokenJwt, validate_token

get_roles_router = APIRouter()


@get_roles_router.get("/", response_model=GetRolesResponse)
@check_role(Permission.CAN_ADMINISTER)
async def get_roles(
    offset: int = 0,
    limit: int | None = None,
    only_name: bool = False,
    token: TokenJwt = Depends(validate_token),
):
    """
    Get list of roles.

    **Permission**: can_administer
    """

    roles_query = Role.exclude(id=token.role_id)
    total_count = await roles_query.count()

    if not limit:
        limit = (
            total_count - offset
            if only_name
            else Session.config.DEFAULT_LIMIT_VALUE
        )

    roles = await roles_query.offset(offset).limit(limit)

    return GetRolesResponse(
        total_count=total_count,
        roles=[
            RoleName(**await role.to_dict_name())
            if only_name
            else RoleModel(**await role.to_dict())
            for role in roles
        ],
    )
