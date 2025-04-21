from fastapi import APIRouter, Depends
from tortoise.transactions import in_transaction

from backend.database.models import Printer
from backend.decorators import check_role
from backend.models.error import NotFound
from backend.models.printers import GetPrinterResponse
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

get_printer_router = APIRouter()


@get_printer_router.get("/{printer_id}", response_model=GetPrinterResponse)
@check_role(Permission.CAN_ADMINISTER)
async def get_printer(
    printer_id: int, token: TokenJwt = Depends(validate_token)
):
    """
    Get information about a printer.

    **Permission**: can_administer
    """

    async with in_transaction() as connection:
        printer = await Printer.get_or_none(id=printer_id, using_db=connection)

        if not printer:
            raise NotFound(code=ErrorCodes.PRINTER_NOT_FOUND)

    return GetPrinterResponse(**await printer.to_dict())
