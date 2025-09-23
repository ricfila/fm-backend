from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from backend.database.models import Ticket
from backend.decorators import check_role
from backend.models.base import BaseResponse
from backend.models.error import Conflict
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

delete_tickets_router = APIRouter()


@delete_tickets_router.delete("/{order_id}/tickets", response_model=BaseResponse)
@check_role(Permission.CAN_ADMINISTER)
async def delete_tickets(
    order_id: int,
    token: TokenJwt = Depends(validate_token)
):
    """
    Delete all the tickets of an order.

    **Permission**: can_administer
    """

    async with in_transaction() as connection:
        tickets = await Ticket.filter(order_id=order_id).using_db(connection)

        for ticket in tickets:
            try:
                await ticket.delete(using_db=connection)
            except IntegrityError:
                raise Conflict(code=ErrorCodes.TICKET_UPDATE_FAILED)
        
    return BaseResponse()


