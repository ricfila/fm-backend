import datetime

from pydantic import BaseModel, Field, field_validator

from backend.models import BaseResponse
from backend.models.products import Product
from backend.utils import validate_name_field, validate_short_name_field


class MenuDate(BaseModel):
    id: int
    start_date: datetime.datetime
    end_date: datetime.datetime


class MenuFieldProduct(BaseModel):
    id: int
    price: float
    product_id: int


class MenuField(BaseModel):
    id: int
    name: str
    max_sortable_elements: int
    additional_cost: float
    is_optional: bool
    products: list[MenuFieldProduct] | None = None


class MenuRole(BaseModel):
    id: int
    role_id: int


class Menu(BaseModel):
    id: int
    name: str
    short_name: str
    price: float
    dates: list[MenuDate] | None = None
    fields: list[MenuField] | None = None
    roles: list[MenuRole] | None = None


class AddMenuDateItem(BaseModel):
    start_date: datetime.datetime
    end_date: datetime.datetime


class AddMenuDateResponse(BaseResponse):
    date: MenuDate


class AddMenuFieldItem(BaseModel):
    name: str
    max_sortable_elements: int = Field(ge=1)
    additional_cost: float = Field(ge=0)

    @field_validator("name")
    @classmethod
    def validate_name_field(cls, name: str):
        return validate_name_field(name)


class AddMenuFieldResponse(BaseResponse):
    field: MenuField


class AddMenuFieldProductItem(BaseModel):
    product_id: int
    price: float = Field(ge=0)


class AddMenuFieldProductResponse(BaseResponse):
    field_product: MenuFieldProduct


class AddMenuRoleItem(BaseModel):
    role_id: int


class AddMenuRoleResponse(BaseResponse):
    role: MenuRole


class CreateMenuItem(BaseModel):
    name: str
    short_name: str
    price: float = Field(ge=0)

    @field_validator("name")
    @classmethod
    def validate_name_field(cls, name: str):
        return validate_name_field(name)

    @field_validator("short_name")
    @classmethod
    def validate_short_name_field(cls, short_name: str):
        return validate_short_name_field(short_name)


class CreateMenuResponse(BaseResponse):
    menu: Menu


class GetMenuResponse(BaseResponse, Menu):
    pass


class GetMenuProductsResponse(BaseResponse):
    products: list[Product]


class GetMenusResponse(BaseResponse):
    total_count: int
    menus: list[Menu]


class UpdateMenuFieldAdditionalCostItem(BaseModel):
    additional_cost: float = Field(ge=0)


class UpdateMenuFieldIsOptionalItem(BaseModel):
    is_optional: bool


class UpdateMenuFieldMaxSortableElementsItem(BaseModel):
    max_sortable_elements: int = Field(ge=1)


class UpdateMenuFieldNameItem(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def validate_name_field(cls, name: str):
        return validate_name_field(name)


class UpdateMenuNameItem(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def validate_name_field(cls, name: str):
        return validate_name_field(name)


class UpdateMenuShortNameItem(BaseModel):
    short_name: str

    @field_validator("short_name")
    @classmethod
    def validate_short_name_field(cls, short_name: str):
        return validate_short_name_field(short_name)


class UpdateMenuPriceItem(BaseModel):
    price: float = Field(ge=0)
