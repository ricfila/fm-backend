from fastapi import APIRouter, Depends
from tortoise.transactions import in_transaction

from backend.database.models import Role, RolePrinter
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import NotFound
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

delete_role_printer_router = APIRouter()


@delete_role_printer_router.delete(
    "/{role_id}/printer/{role_printer_id}", response_model=BaseResponse
)
@check_role(Permission.CAN_ADMINISTER)
async def delete_role_printer(
    role_id: int,
    role_printer_id: int,
    token: TokenJwt = Depends(validate_token),
):
    """
    Delete a role printer from the id.

    **Permission**: can_administer
    """

    async with in_transaction() as connection:
        role = await Role.get_or_none(id=role_id, using_db=connection)

        if not role:
            raise NotFound(code=ErrorCodes.ROLE_NOT_FOUND)

        role_printer = await RolePrinter.get_or_none(
            id=role_printer_id, role=role, using_db=connection
        )

        if not role_printer:
            raise NotFound(code=ErrorCodes.ROLE_PRINTER_NOT_FOUND)

        await role_printer.delete(using_db=connection)

    return BaseResponse()
