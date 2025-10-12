from datetime import datetime

from fastapi import APIRouter, Depends, Query
from tortoise.transactions import in_transaction
from tortoise.expressions import Q

from backend.database.models import Ticket
from backend.models.orders import TicketOrder, GetTicketsResponse
from backend.models.tickets import Ticket as TicketModel
from backend.models.error import NotFound
from backend.utils import ErrorCodes, TokenJwt, validate_token

get_tickets_router = APIRouter()


@get_tickets_router.get("/", response_model=GetTicketsResponse)
async def get_tickets(
    from_date: datetime = None,
    to_date: datetime = None,
    include_order: bool = False,
    is_confirmed: bool = None,
    is_printed: bool = None,
    is_completed: bool = None,
    categories: list[int] = Query(default=[]),
    token: TokenJwt = Depends(validate_token)
):
    """
    Get all the tickets.
    """

    async with in_transaction() as connection:
        query = Q(order__is_deleted=False)

        #if from_date is not None:
        #    query &= Q(order__created_at__ge=from_date)

        #if to_date is not None:
        #    query &= Q(order__created_at__lt=to_date)

        if is_confirmed is not None:
            query &= Q(order__is_confirmed=is_confirmed)

        if is_printed is not None:
            query &= Q(printed_at__isnull=not is_printed)

        if is_completed is not None:
            query &= Q(completed_at__isnull=not is_completed)

        if categories:
            query &= Q(category_id__in=categories)

        tickets = await Ticket.filter(query).prefetch_related("order", "order__user", "order__confirmed_by").using_db(connection)

        if not tickets:
            raise NotFound(code=ErrorCodes.TICKET_NOT_FOUND)

    return GetTicketsResponse(
        total_count=len(tickets),
        tickets=[
            TicketOrder(**await ticket.to_dict_order())
            if include_order else
            TicketModel(**await ticket.to_dict())
            for ticket in tickets
        ]
    )
