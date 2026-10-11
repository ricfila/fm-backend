from fastapi import APIRouter, Depends
from tortoise.transactions import in_transaction

from backend.config import Session
from backend.database.models import Order, Ticket
from backend.decorators import check_role
from backend.models.error import NotFound
from backend.models import BaseResponse
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

print_ticket_router = APIRouter()


@print_ticket_router.get("/{ticket_id}/print", response_model=BaseResponse)
@check_role(
    Permission.CAN_ORDER,
    Permission.CAN_COMPLETE_TICKETS,
    Permission.CAN_CONFIRM_ORDERS,
)
async def print_ticket(
    ticket_id: int,
    printer_id: int = None,
    token: TokenJwt = Depends(validate_token),
):
    """
    Print a ticket.

     **Permission**: can_order, can_complete_tickets, can_confirm_orders
    """

    async with in_transaction() as connection:
        ticket = (
            await Ticket.get_or_none(id=ticket_id)
            .prefetch_related(*Session.print_manager.prefetch_values)
            .using_db(connection)
        )

        if not ticket:
            raise NotFound(ErrorCodes.TICKET_NOT_FOUND)

        update_db = bool(ticket.printed_at is None)

        await Session.print_manager.print_ticket(ticket, update_db, printer_id)

    return BaseResponse()
