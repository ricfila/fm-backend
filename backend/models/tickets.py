from pydantic import BaseModel

from backend.models.base import BaseResponse
from backend.models.categories import CategoryName


class Ticket(BaseModel):
    id: int
    order_id: int
    category_id: int
    is_printed: bool


class TicketCategory(BaseModel):
    id: int
    category: CategoryName
    is_printed: bool


class GetTicketsResponse(BaseResponse):
    total_count: int
    tickets: list[Ticket | TicketCategory]
