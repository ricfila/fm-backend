from pydantic import BaseModel, field_validator

from backend.models import BaseResponse
from backend.utils import validate_name_field


class Subcategory(BaseModel):
    id: int
    name: str
    order: int


class SubcategoryName(BaseModel):
    id: int
    name: str


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
