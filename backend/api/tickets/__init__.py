__all__ = (
    "tickets",
    "delete_ticket_router",
    "update_ticket_router",
)

from fastapi import APIRouter

from .delete_ticket import delete_ticket_router
from .update_ticket import update_ticket_router

tickets = APIRouter(prefix="/tickets", tags=["tickets"])
tickets.include_router(delete_ticket_router)
tickets.include_router(update_ticket_router)
