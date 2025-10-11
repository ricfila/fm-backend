import datetime
import pytz

from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from backend.database.models import Ticket
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import Conflict, NotFound
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

update_ticket_printed_router = APIRouter()


@update_ticket_printed_router.put("/{ticket_id}/printed", response_model=BaseResponse)
@check_role(Permission.CAN_ADMINISTER)
async def update_ticket(
    ticket_id: int,
    is_printed: bool,
    token: TokenJwt = Depends(validate_token)
):
    """
    Update a ticket printed status.

     **Permission**: can_administer
    """

    async with in_transaction() as connection:
        ticket = await Ticket.get_or_none(id=ticket_id, using_db=connection)

        if not ticket:
            raise NotFound(code=ErrorCodes.TICKET_NOT_FOUND)

        rome_tz = pytz.timezone("Europe/Rome")
        now_in_rome = datetime.datetime.now(rome_tz)

        ticket.printed_at = now_in_rome if is_printed else None

        try:
            await ticket.save(using_db=connection)
        except IntegrityError:
            raise Conflict(code=ErrorCodes.TICKET_UPDATE_FAILED)

    return BaseResponse()
