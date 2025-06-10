from pydantic import BaseModel, field_validator

from backend.models import BaseResponse
from backend.utils import validate_name_field, validate_order_field


class Subcategory(BaseModel):
    id: int
    name: str
    order: int
    include_cover_charge: bool


class SubcategoryName(BaseModel):
    id: int
    name: str
    include_cover_charge: bool


class CreateSubcategoryItem(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def validate_name_field(cls, name: str):
        return validate_name_field(name)


class CreateSubcategoryResponse(BaseResponse):
    subcategory: Subcategory


class GetSubcategoriesResponse(BaseResponse):
    total_count: int
    subcategories: list[Subcategory | SubcategoryName]


class GetSubcategoryResponse(BaseResponse, Subcategory):
    pass


class UpdateSubcategoryNameItem(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def validate_name_field(cls, name: str):
        return validate_name_field(name)


class UpdateSubcategoryOrderItem(BaseModel):
    order: int

    @field_validator("order")
    @classmethod
    def validate_order_field(cls, order: int):
        return validate_order_field(order)


class UpdateSubcategoryIncludeCoverChargeItem(BaseModel):
    include_cover_charge: bool
