import datetime
from pydantic import BaseModel

from backend.models.base import BaseResponse
from backend.models.categories import CategoryName


class Ticket(BaseModel):
    id: int
    order_id: int
    category_id: int
    printed_at: datetime.datetime


class TicketCategory(BaseModel):
    id: int
    category: CategoryName
    printed_at: datetime.datetime


class GetTicketsResponse(BaseResponse):
    total_count: int
    tickets: list[Ticket | TicketCategory]
