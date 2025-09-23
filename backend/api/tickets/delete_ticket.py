from fastapi import APIRouter, Depends
from tortoise.transactions import in_transaction

from backend.database.models import Ticket
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import NotFound
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

delete_ticket_router = APIRouter()


@delete_ticket_router.delete("/{ticket_id}", response_model=BaseResponse)
@check_role(Permission.CAN_ADMINISTER)
async def delete_ticket(
    ticket_id: int,
    token: TokenJwt = Depends(validate_token)
):
    """
    Delete a ticket from the id.

     **Permission**: can_administer
    """

    async with in_transaction() as connection:
        ticket = await Ticket.get_or_none(id=ticket_id, using_db=connection)

        if not ticket:
            raise NotFound(code=ErrorCodes.TICKET_NOT_FOUND)

        await ticket.delete(using_db=connection)

    return BaseResponse()
