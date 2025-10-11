from fastapi import APIRouter, Depends
from tortoise.transactions import in_transaction

from backend.database.models import Ticket
from backend.models.orders import GetTicketsResponse, TicketCategory
from backend.models.tickets import Ticket as TicketModel
from backend.models.error import NotFound
from backend.utils import ErrorCodes, TokenJwt, validate_token

get_order_tickets_router = APIRouter()


@get_order_tickets_router.get("/{order_id}/tickets", response_model=GetTicketsResponse)
async def get_order_tickets(
    order_id: int,
    include_category_name: bool = False,
    token: TokenJwt = Depends(validate_token)
):
    """
    Get all the tickets of an order.
    """

    async with in_transaction() as connection:
        tickets = await Ticket.filter(order_id=order_id).using_db(connection)

        if not tickets:
            raise NotFound(code=ErrorCodes.TICKET_NOT_FOUND)

    return GetTicketsResponse(
        total_count=len(tickets),
        tickets=[
            TicketCategory(**await ticket.to_dict_category())
            if include_category_name
            else TicketModel(**await ticket.to_dict())
            for ticket in tickets
        ]
    )


