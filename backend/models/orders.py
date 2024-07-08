from pydantic import BaseModel, Field, field_validator

from backend.utils import validate_name_field


class CreateOrderProductItem(BaseModel):
    product_id: int
    variant_id: int | None = None
    ingredients: list[int] | None = []
    quantity: int | None = Field(ge=1, default=None)

    _price: int = 0


class CreateOrderMenuFieldItem(BaseModel):
    menu_field_id: int
    products: list[CreateOrderProductItem]


class CreateOrderMenuItem(BaseModel):
    menu_id: int
    fields: list[CreateOrderMenuFieldItem]
    quantity: int = Field(ge=1)

    _price: int = 0


class CreateOrderItem(BaseModel):
    customer: str
    guests: int | None = Field(ge=1, default=None)
    is_take_away: bool
    table: int | None = Field(ge=1, default=None)
    products: list[CreateOrderProductItem] | None = []
    menus: list[CreateOrderMenuItem] | None = []

    @field_validator("customer")
    @classmethod
    def validate_customer_field(cls, customer: str):
        return validate_name_field(customer)
