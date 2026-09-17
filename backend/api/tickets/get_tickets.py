from fastapi import APIRouter, Depends, Query
from tortoise.transactions import in_transaction
from tortoise.expressions import Q

from backend.database.models import Ticket
from backend.models.orders import GetTicketsResponse, TicketOrder
from backend.models.tickets import Ticket as TicketModel
from backend.models.error import BadRequest, NotFound
from backend.utils import ErrorCodes, TokenJwt, validate_token

get_tickets_router = APIRouter()


@get_tickets_router.get("/", response_model=GetTicketsResponse)
async def get_tickets(
    include_order: bool = False,
    categories: list[int] = Query(default=[]),
    need_confirmation: bool = None,
    confirmed: bool = None,
    is_printed: bool = None,
    is_completed: bool = None,
    token: TokenJwt = Depends(validate_token)
):
    """
    Get all the tickets.
    """

    if need_confirmation == False and confirmed is not None:
        raise BadRequest(code=ErrorCodes.INVALID_QUERY_PARAMS)


    async with in_transaction() as connection:
        query = Q(order__is_deleted=False)

        #if from_date is not None:
        #    query &= Q(order__created_at__ge=from_date)

        #if to_date is not None:
        #    query &= Q(order__created_at__lt=to_date)

        if categories:
            query &= Q(category_id__in=categories)

        if need_confirmation is not None and confirmed is None:
            query &= Q(order__needs_confirmation=need_confirmation)

        if confirmed is not None:
            query &= Q(order__needs_confirmation=True)
            query &= Q(order__confirmed_at__isnull=not confirmed)

        if is_printed is not None:
            query &= Q(printed_at__isnull=not is_printed)

        if is_completed is not None:
            query &= Q(completed_at__isnull=not is_completed)

        tickets = await Ticket.filter(query).prefetch_related(
            "order",
            "order__user",
            "order__confirmed_by"
        ).using_db(connection)

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
