__all__ = (
    "tickets",
    "delete_ticket_router",
    "update_ticket_completed_router",
    "update_ticket_printed_router",
)

from fastapi import APIRouter

from .delete_ticket import delete_ticket_router
from .update_ticket_printed import update_ticket_printed_router
from .update_ticket_completed import update_ticket_completed_router

tickets = APIRouter(prefix="/tickets", tags=["tickets"])
tickets.include_router(delete_ticket_router)
tickets.include_router(update_ticket_printed_router)
tickets.include_router(update_ticket_completed_router)
