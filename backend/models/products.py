import datetime

from pydantic import BaseModel, Field, field_validator

from backend.models import BaseResponse
from backend.utils import (
    Category,
    validate_name_field,
    validate_short_name_field,
    validate_order_field,
)


class ProductDate(BaseModel):
    id: int
    start_date: datetime.datetime
    end_date: datetime.datetime


class ProductIngredient(BaseModel):
    id: int
    ingredient_id: int
    name: str
    price: float
    max_quantity: float
    is_default: bool


class ProductRole(BaseModel):
    id: int
    role_id: int


class ProductVariant(BaseModel):
    id: int
    name: str
    price: float


class Product(BaseModel):
    id: int
    name: str
    short_name: str
    is_priority: bool
    is_main: bool
    price: float
    category_id: int
    subcategory_id: int
    order: int
    daily_max_sales: int | None
    color: str | None
    dates: list[ProductDate] | None = None
    ingredients: list[ProductIngredient] | None = None
    roles: list[ProductRole] | None = None
    variants: list[ProductVariant] | None = None


class ProductName(BaseModel):
    id: int
    name: str
    short_name: str


class AddProductDateItem(BaseModel):
    start_date: datetime.datetime
    end_date: datetime.datetime


class AddProductDateResponse(BaseResponse):
    date: ProductDate


class AddProductIngredientItem(BaseModel):
    ingredient_id: int
    price: float = Field(ge=0)
    max_quantity: float = Field(gt=0)
    is_default: bool


class AddProductIngredientResponse(BaseResponse):
    product_ingredient: ProductIngredient


class AddProductRoleItem(BaseModel):
    role_id: int


class AddProductRoleResponse(BaseResponse):
    role: ProductRole


class AddProductVariantItem(BaseModel):
    name: str
    price: float = Field(ge=0)


class AddProductVariantResponse(BaseResponse):
    variant: ProductVariant


class CreateProductItem(BaseModel):
    name: str
    short_name: str
    price: float = Field(ge=0)
    category_id: int
    subcategory_id: int

    @field_validator("name")
    @classmethod
    def validate_name_field(cls, name: str):
        return validate_name_field(name)

    @field_validator("short_name")
    @classmethod
    def validate_short_name_field(cls, short_name: str):
        return validate_short_name_field(short_name)


class CreateProductResponse(BaseResponse):
    product: Product


class GetProductResponse(BaseResponse, Product):
    pass


class GetProductsResponse(BaseResponse):
    total_count: int
    products: list[Product | ProductName]


class UpdateProductNameItem(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def validate_name_field(cls, name: str):
        return validate_name_field(name)


class UpdateProductOrderItem(BaseModel):
    order: int

    @field_validator("order")
    @classmethod
    def validate_order_field(cls, order: int):
        return validate_order_field(order)


class UpdateProductShortNameItem(BaseModel):
    short_name: str

    @field_validator("short_name")
    @classmethod
    def validate_short_name_field(cls, short_name: str):
        return validate_short_name_field(short_name)


class UpdateProductIsPriorityItem(BaseModel):
    is_priority: bool


class UpdateProductPriceItem(BaseModel):
    price: float = Field(ge=0)


class UpdateProductCategoryItem(BaseModel):
    category_id: int


class UpdateProductDailyMaxSalesItem(BaseModel):
    daily_max_sales: int | None = Field(ge=0)


class UpdateProductSubcategoryItem(BaseModel):
    subcategory_id: int

class UpdateProductIngredientItem(BaseModel):
    price: float = Field(ge=0)
    max_quantity: float = Field(gt=0)
    is_default: bool
