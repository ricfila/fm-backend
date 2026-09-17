import datetime
from pydantic import BaseModel

from backend.models.categories import CategoryName


class Ticket(BaseModel):
    id: int
    order_id: int
    category_id: int
    printed_at: datetime.datetime | None
    completed_at: datetime.datetime | None
    has_collapsed_categories: bool


class TicketCategory(BaseModel):
    id: int
    category: CategoryName
    printed_at: datetime.datetime | None
    completed_at: datetime.datetime | None
    has_collapsed_categories: bool


class GetTicketsItem(BaseModel):
    pass


class UpdateTicketCompletedItem(BaseModel):
    is_completed: bool


class UpdateTicketPrintedItem(BaseModel):
    is_printed: bool
