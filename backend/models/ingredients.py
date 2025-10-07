import datetime
from pydantic import BaseModel, field_validator

from backend.models import BaseResponse
from backend.utils import validate_name_field


class Ingredient(BaseModel):
    id: int
    name: str
    ward: str
    is_monitored: bool
    sell_if_stocked: bool
    cooking_time: int | None
    target_quantity: float | None


class IngredientName(BaseModel):
    id: int
    name: str


class IngredientStock(BaseModel):
    id: int
    name: str
    ward: str
    is_monitored: bool
    sell_if_stocked: bool
    cooking_time: int | None
    target_quantity: float | None
    added_stock: float | None = None
    consumed_stock: float | None = None
    stock_starting_from: datetime.datetime | None = None


class CreateIngredientItem(BaseModel):
    name: str
    ward: str
    is_monitored: bool
    sell_if_stocked: bool
    cooking_time: int | None
    target_quantity: float | None

    @field_validator("name")
    @classmethod
    def validate_name_field(cls, name: str):
        return validate_name_field(name)

    @field_validator("ward")
    @classmethod
    def validate_ward_field(cls, ward: str):
        return validate_name_field(ward)


class CreateIngredientResponse(BaseResponse):
    ingredient: Ingredient


class GetIngredientResponse(BaseResponse, Ingredient):
    pass


class GetIngredientStockResponse(BaseResponse, IngredientStock):
    pass


class GetIngredientsResponse(BaseResponse):
    total_count: int
    ingredients: list[Ingredient | IngredientName | IngredientStock]


class GetWardsResponse(BaseResponse):
    total_count: int
    wards: list[str]


class Stock(BaseModel):
    id: int
    ingredient_id: int
    quantity: float
    available_from: str


class AddStockItem(BaseModel):
    quantity: float


class AddStockResponse(BaseResponse):
    stock: Stock


class UpdateStockItem(BaseModel):
    quantity: float | None = None


class StockListResponse(BaseResponse):
    total_quantity: float
    stocks: list[Stock]
