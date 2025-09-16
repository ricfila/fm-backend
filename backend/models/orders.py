import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator

from backend.models import BaseResponse
from backend.models.menu import Menu
from backend.models.payment_methods import PaymentMethodName
from backend.models.products import Product
from backend.models.users import User
from backend.utils import validate_name_field, PrinterType


class OrderProductIngredient(BaseModel):
    id: int
    ingredient_id: int
    quantity: Decimal = Field(ge=1, default=Decimal("0.00"))


class OrderProduct(BaseModel):
    id: int
    product_id: int
    price: float
    quantity: int
    notes: str | None = None
    variant_id: int | None = None
    order_menu_field_id: int | None = None
    product: Product | None = None
    ingredients: list[OrderProductIngredient] | None = None


class OrderMenuField(BaseModel):
    id: int
    menu_field_id: int
    products: list[OrderProduct] | None = None


class OrderMenu(BaseModel):
    id: int
    price: float
    quantity: int
    menu: Menu | None = None
    fields: list[OrderMenuField] | None = None


class Order(BaseModel):
    id: int
    customer: str
    guests: int | None = Field(ge=1, default=None)
    is_take_away: bool
    table: str | None = None
    is_confirmed: bool
    is_done: bool
    is_voucher: bool
    notes: str | None = None
    price: float
    payment_method: PaymentMethodName | None = None
    user: User | None = None
    confirmed_by: User | None = None
    menus: list[OrderMenu] | None = None
    products: list[OrderProduct] | None = None
    created_at: datetime.datetime


class ConfirmOrderItem(BaseModel):
    table: str


class CreateOrderProductIngredientItem(BaseModel):
    ingredient_id: int
    quantity: Decimal = Field(ge=1, default=Decimal("0.00"))


class CreateOrderProductItem(BaseModel):
    product_id: int
    variant_id: int | None = None
    ingredients: list[CreateOrderProductIngredientItem] = Field(default=[])
    quantity: int = Field(ge=1)
    notes: str | None = None

    _price: Decimal = Decimal("0.00")
    _has_cover_charge: bool


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
    table: str | None = None
    is_voucher: bool
    notes: str | None = None
    parent_order_id: int | None = None
    payment_method_id: int
    products: list[CreateOrderProductItem] = Field(default=[])
    menus: list[CreateOrderMenuItem] = Field(default=[])

    @field_validator("customer")
    @classmethod
    def validate_customer_field(cls, customer: str):
        return validate_name_field(customer)


class CreateOrderResponse(BaseResponse):
    order: Order


class GetOrderResponse(BaseResponse, Order):
    pass


class GetOrdersResponse(BaseResponse):
    total_count: int
    orders: list[Order]


class PrintOrderItem(BaseModel):
    printer_types: list[PrinterType] | None = None
