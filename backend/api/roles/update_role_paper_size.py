from fastapi import APIRouter, Depends
from tortoise.transactions import in_transaction

from backend.database.models import Role
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import NotFound, Unauthorized
from backend.models.roles import UpdateRolePaperSizeItem
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

update_role_paper_size_router = APIRouter()


@update_role_paper_size_router.put(
    "/{role_id}/paper_size", response_model=BaseResponse
)
@check_role(Permission.CAN_ADMINISTER)
async def update_role_paper_size(
    role_id: int,
    item: UpdateRolePaperSizeItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Update paper size of role.

    **Permission**: can_administer
    """

    async with in_transaction() as connection:
        role = await Role.get_or_none(id=role_id, using_db=connection)

        if not role:
            raise NotFound(code=ErrorCodes.ROLE_NOT_FOUND)

        if role.name == "admin":
            raise Unauthorized(code=ErrorCodes.NOT_ALLOWED)

        role.paper_size = item.paper_size

        await role.save(using_db=connection)

    return BaseResponse()
