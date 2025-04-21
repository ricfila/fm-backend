from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from backend.database.models import Printer
from backend.decorators import check_role
from backend.models.error import Conflict
from backend.models.printers import (
    CreatePrinterResponse,
    CreatePrinterItem,
    Printer as PrinterModel,
)
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

create_printer_router = APIRouter()


@create_printer_router.post("/", response_model=CreatePrinterResponse)
@check_role(Permission.CAN_ADMINISTER)
async def create_printer(
    item: CreatePrinterItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Create a new printer.

    **Permission**: can_administer
    """

    async with in_transaction() as connection:
        new_printer = Printer(name=item.name, ip_address=item.ip_address)

        try:
            await new_printer.save(using_db=connection)

        except IntegrityError:
            raise Conflict(code=ErrorCodes.PRINTER_ALREADY_EXISTS)

    return CreatePrinterResponse(
        printer=PrinterModel(**await new_printer.to_dict())
    )
