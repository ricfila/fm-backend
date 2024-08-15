from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from backend.database.models import Role
from backend.decorators import check_role
from backend.models.error import Conflict
from backend.models.roles import CreateRoleItem, CreateRoleResponse
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

create_role_router = APIRouter()


@create_role_router.post("/", response_model=CreateRoleResponse)
@check_role(Permission.CAN_ADMINISTER)
async def create_role(
    item: CreateRoleItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Create a new role.

    **Permission**: can_administer
    """

    async with in_transaction() as connection:
        new_role = Role(name=item.name)

        try:
            await new_role.save(using_db=connection)

        except IntegrityError:
            raise Conflict(code=ErrorCodes.ROLE_ALREADY_EXISTS)

    return CreateRoleResponse(role=await new_role.to_dict())
