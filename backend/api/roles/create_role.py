from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError

from backend.database.models import Role
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import Conflict
from backend.models.roles import CreateRoleItem
from backend.utils import Permission, TokenJwt, validate_token

create_role_router = APIRouter()


@create_role_router.post("/", response_model=BaseResponse)
@check_role(Permission.CAN_ADMINISTER)
async def create_role(
    item: CreateRoleItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Create a new role.

    **Permission**: can_administer
    """

    new_role = Role(name=item.name, paper_size=item.paper_size)

    for permission, value in item.permissions.items():
        setattr(new_role, permission, value)

    try:
        await new_role.save()

    except IntegrityError:
        raise Conflict("Role already exists")

    return BaseResponse()
