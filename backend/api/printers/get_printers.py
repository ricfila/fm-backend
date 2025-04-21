from fastapi import APIRouter, Depends
from tortoise.exceptions import ParamsError
from tortoise.expressions import Q
from tortoise.transactions import in_transaction

from backend.database.models import Printer
from backend.decorators import check_role
from backend.models.error import BadRequest
from backend.models.printers import (
    GetPrintersResponse,
    Printer as PrinterModel,
    PrinterName,
)
from backend.utils import Permission, TokenJwt, validate_token, ErrorCodes
from backend.utils.query_utils import process_query_with_pagination

get_printers_router = APIRouter()


@get_printers_router.get("/", response_model=GetPrintersResponse)
@check_role(Permission.CAN_ADMINISTER)
async def get_printers(
    offset: int = 0,
    limit: int | None = None,
    only_name: bool = False,
    order_by: str = None,
    token: TokenJwt = Depends(validate_token),
):
    """
    Get list of printers.

    **Permission**: can_administer
    """

    async with in_transaction() as connection:
        (
            printer_query,
            total_count,
            limit,
        ) = await process_query_with_pagination(
            Printer, Q(), connection, offset, limit, order_by
        )

        try:
            printers = await printer_query.offset(offset).limit(limit)
        except ParamsError:
            raise BadRequest(code=ErrorCodes.INVALID_OFFSET_OR_LIMIT_NEGATIVE)

    return GetPrintersResponse(
        total_count=total_count,
        printers=[
            PrinterName(**await printer.to_dict_name())
            if only_name
            else PrinterModel(**await printer.to_dict())
            for printer in printers
        ],
    )
