import datetime
from pydantic import BaseModel


class Ticket(BaseModel):
    id: int
    order_id: int
    category_id: int
    printed_at: datetime.datetime | None
    completed_at: datetime.datetime | None


class GetTicketsItem(BaseModel):
    pass


class UpdateTicketCompletedItem(BaseModel):
    is_completed: bool


class UpdateTicketPrintedItem(BaseModel):
    is_printed: bool
