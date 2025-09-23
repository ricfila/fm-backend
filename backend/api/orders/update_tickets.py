from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from backend.database.models import Ticket
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import Conflict, NotFound
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

update_tickets_router = APIRouter()


@update_tickets_router.put("/{order_id}/tickets", response_model=BaseResponse)
@check_role(Permission.CAN_ADMINISTER)
async def update_tickets(
    order_id: int,
    is_printed: bool,
    token: TokenJwt = Depends(validate_token)
):
    """
    Update all the tickets of an order.

    **Permission**: can_administer
    """

    async with in_transaction() as connection:
        tickets = await Ticket.filter(order_id=order_id).using_db(connection)

        if not tickets:
            raise NotFound(code=ErrorCodes.TICKET_NOT_FOUND)

        for ticket in tickets:
            ticket.is_printed = is_printed

        try:
            await Ticket.bulk_update(objects=tickets, fields=['is_printed'], using_db=connection)
        except IntegrityError:
            raise Conflict(code=ErrorCodes.TICKET_UPDATE_FAILED)

    return BaseResponse()
