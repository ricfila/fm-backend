from fastapi import APIRouter, Depends
from tortoise.transactions import in_transaction

from backend.database.models import Role
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import NotFound, Unauthorized
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

delete_role_router = APIRouter()


@delete_role_router.delete("/{role_id}", response_model=BaseResponse)
@check_role(Permission.CAN_ADMINISTER)
async def delete_role(role_id: int, token: TokenJwt = Depends(validate_token)):
    """
    Delete a role from the id.

    **Permission**: can_administer
    """

    async with in_transaction() as connection:
        role = await Role.get_or_none(id=role_id, using_db=connection)

        if not role:
            raise NotFound(code=ErrorCodes.ROLE_NOT_FOUND)

        if role.name == "admin":
            raise Unauthorized(code=ErrorCodes.NOT_ALLOWED)

        if role.name == "base":
            raise Unauthorized(code=ErrorCodes.NOT_ALLOWED)

        await role.delete(using_db=connection)

    return BaseResponse()
