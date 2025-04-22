from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from backend.database.models import Role, RolePrinter, Printer
from backend.decorators import check_role
from backend.models.error import Conflict, NotFound
from backend.models.roles import AddRolePrinterResponse, AddRolePrinterItem
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

add_role_printer_router = APIRouter()


@add_role_printer_router.post(
    "/{role_id}/printer", response_model=AddRolePrinterResponse
)
@check_role(Permission.CAN_ADMINISTER)
async def add_role_printer(
    role_id: int,
    item: AddRolePrinterItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Add role printer.

    **Permission**: can_administer
    """

    async with in_transaction() as connection:
        role = await Role.get_or_none(id=role_id, using_db=connection)

        if not role:
            raise NotFound(code=ErrorCodes.ROLE_NOT_FOUND)

        printer = await Printer.get_or_none(
            id=item.printer_id, using_db=connection
        )

        if not printer:
            raise NotFound(code=ErrorCodes.PRINTER_NOT_FOUND)

        new_role_printer = RolePrinter(
            role=role, printer=printer, printer_type=item.printer_type
        )

        try:
            await new_role_printer.save(using_db=connection)

        except IntegrityError:
            raise Conflict(code=ErrorCodes.ROLE_PRINTER_ALREADY_EXISTS)

    return AddRolePrinterResponse(printer=await new_role_printer.to_dict())
