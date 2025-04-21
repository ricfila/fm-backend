from fastapi import APIRouter, Depends
from tortoise.transactions import in_transaction

from backend.database.models import Printer
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import NotFound
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

delete_printer_router = APIRouter()


@delete_printer_router.delete("/{printer_id}", response_model=BaseResponse)
@check_role(Permission.CAN_ADMINISTER)
async def delete_printer(
    printer_id: int, token: TokenJwt = Depends(validate_token)
):
    """
    Delete a printer from the id.

    **Permission**: can_administer
    """

    async with in_transaction() as connection:
        printer = await Printer.get_or_none(id=printer_id, using_db=connection)

        if not printer:
            raise NotFound(code=ErrorCodes.PRINTER_NOT_FOUND)

        await printer.delete(using_db=connection)

    return BaseResponse()
