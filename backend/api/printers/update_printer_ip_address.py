from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from backend.database.models import Printer
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import Conflict, NotFound
from backend.models.printers import UpdatePrinterIpAddressItem
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

update_printer_ip_address_router = APIRouter()


@update_printer_ip_address_router.put(
    "/{printer_id}/ip_address", response_model=BaseResponse
)
@check_role(Permission.CAN_ADMINISTER)
async def update_printer_ip_address(
    printer_id: int,
    item: UpdatePrinterIpAddressItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Update ip address of printer.

    **Permission**: can_administer
    """

    async with in_transaction() as connection:
        printer = await Printer.get_or_none(id=printer_id, using_db=connection)

        if not printer:
            raise NotFound(code=ErrorCodes.PRINTER_NOT_FOUND)

        printer.ip_address = item.ip_address

        try:
            await printer.save(using_db=connection)

        except IntegrityError:
            raise Conflict(code=ErrorCodes.PRINTER_ALREADY_EXISTS)

    return BaseResponse()
