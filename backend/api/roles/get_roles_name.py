from fastapi import APIRouter, Depends

from backend.database.models import Role
from backend.decorators import check_role
from backend.models.roles import GetRolesNameResponse
from backend.utils import Permission, TokenJwt, validate_token

get_roles_name_router = APIRouter()


@get_roles_name_router.get("/name", response_model=GetRolesNameResponse)
@check_role(Permission.CAN_ADMINISTER)
async def get_roles_name(token: TokenJwt = Depends(validate_token)):
    """
    Get list of roles name.

    **Permission**: can_administer
    """

    roles_query = Role.exclude(id=token.role_id)
    total_count = await roles_query.count()
    roles = await roles_query.all()

    return GetRolesNameResponse(
        total_count=total_count,
        roles=[{"id": role.id, "name": role.name} for role in roles],
    )
