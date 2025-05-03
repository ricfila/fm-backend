from pydantic import BaseModel

from backend.models import BaseResponse


class StatisticProduct(BaseModel):
    name: str
    quantity: int
    price: float


class Statistic(BaseModel):
    total_orders: int
    total_seated: int
    total_take_away: int
    products: list[StatisticProduct]


class GetStatisticResponse(BaseResponse, Statistic):
    pass
