from pydantic import BaseModel, field_validator

from backend.models import BaseResponse
from backend.utils import validate_name_field


class Ingredient(BaseModel):
    id: int
    name: str
    ward: str
    is_monitored: bool


class IngredientName(BaseModel):
    id: int
    name: str


class CreateIngredientItem(BaseModel):
    name: str
    ward: str
    is_monitored: bool

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


class GetIngredientsResponse(BaseResponse):
    total_count: int
    ingredients: list[Ingredient | IngredientName]


class Stock(BaseModel):
    id: int
    ingredient_id: int
    quantity: float
    available_from: str
    is_last_stock: bool


class AddStockItem(BaseModel):
    quantity: float
    is_last_stock: bool


class AddStockResponse(BaseResponse):
    stock: Stock


class UpdateStockItem(BaseModel):
    quantity: float | None = None
    is_last_stock: bool | None = None


class StockListResponse(BaseResponse):
    total_quantity: float
    stocks: list[Stock]
