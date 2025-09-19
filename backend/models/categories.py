from pydantic import BaseModel, Field, field_validator

from backend.models import BaseResponse
from backend.utils import validate_name_field, validate_order_field


class Category(BaseModel):
    id: int
    name: str
    print_delay: int
    printer_id: int | None
    parent_for_take_away_id: int | None
    parent_for_main_products_id: int | None


class CategoryName(BaseModel):
    id: int
    name: str


class CreateCategoryItem(BaseModel):
    name: str
    print_delay: int = Field(ge=0)

    @field_validator("name")
    @classmethod
    def validate_name_field(cls, name: str):
        return validate_name_field(name)


class CreateCategoryResponse(BaseResponse):
    category: Category


class GetCategoriesResponse(BaseResponse):
    total_count: int
    categories: list[Category | CategoryName]


class GetCategoryResponse(BaseResponse, Category):
    pass


class UpdateCategoryNameItem(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def validate_name_field(cls, name: str):
        return validate_name_field(name)


class UpdateCategoryPrintDelayItem(BaseModel):
    print_delay: int = Field(ge=0)


class UpdateCategoryPrinterItem(BaseModel):
    printer_id: int | None


class UpdateParentCategoryItem(BaseModel):
    parent_category_id: int | None
