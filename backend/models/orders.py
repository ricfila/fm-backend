import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator

from backend.models import BaseResponse
from backend.utils import validate_name_field


class OrderProductIngredient(BaseModel):
    id: int
    product_ingredient_id: int
    quantity: int


class OrderProduct(BaseModel):
    id: int
    product_id: int
    price: float
    quantity: int
    variant_id: int
    ingredients: list[OrderProductIngredient] | None = None


class OrderMenuField(BaseModel):
    id: int
    menu_field_id: int
    products: list[OrderProduct] | None = None


class OrderMenu(BaseModel):
    id: int
    price: float
    quantity: int
    fields: list[OrderMenuField] | None = None


class Order(BaseModel):
    id: int
    customer: str
    guests: int
    is_take_away: bool
    table: int
    user_id: int
    created_at: datetime.datetime
    menus: list[OrderMenu] | None = None
    products: list[OrderProduct] | None = None


class CreateOrderProductIngredientItem(BaseModel):
    ingredient_id: int
    quantity: int = Field(ge=1)


class CreateOrderProductItem(BaseModel):
    product_id: int
    variant_id: int | None = None
    ingredients: list[CreateOrderProductIngredientItem] = Field(default=[])
    quantity: int = Field(ge=1)

    _price: Decimal = Decimal("0.00")


class CreateOrderMenuFieldItem(BaseModel):
    menu_field_id: int
    products: list[CreateOrderProductItem]


class CreateOrderMenuItem(BaseModel):
    menu_id: int
    fields: list[CreateOrderMenuFieldItem]
    quantity: int = Field(ge=1)

    _price: Decimal = Decimal("0.00")


class CreateOrderItem(BaseModel):
    customer: str
    guests: int | None = Field(ge=1, default=None)
    is_take_away: bool
    table: int | None = Field(ge=1, default=None)
    products: list[CreateOrderProductItem] = Field(default=[])
    menus: list[CreateOrderMenuItem] = Field(default=[])

    @field_validator("customer")
    @classmethod
    def validate_customer_field(cls, customer: str):
        return validate_name_field(customer)


class CreateOrderResponse(BaseResponse):
    order: Order


class GetOrdersResponse(BaseResponse):
    total_count: int
    orders: list[Order]
