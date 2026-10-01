from pydantic import BaseModel, field_validator

from backend.models import BaseResponse
from backend.utils import validate_name_field, validate_order_field


class Subgroup(BaseModel):
    id: int
    name: str
    order: int
    include_cover_charge: bool


class SubgroupName(BaseModel):
    id: int
    name: str
    include_cover_charge: bool


class CreateSubgroupItem(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def validate_name_field(cls, name: str):
        return validate_name_field(name)


class CreateSubgroupResponse(BaseResponse):
    subgroup: Subgroup


class GetSubgroupsResponse(BaseResponse):
    total_count: int
    subgroups: list[Subgroup | SubgroupName]


class GetSubgroupResponse(BaseResponse, Subgroup):
    pass


class UpdateSubgroupNameItem(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def validate_name_field(cls, name: str):
        return validate_name_field(name)


class UpdateSubgroupOrderItem(BaseModel):
    order: int

    @field_validator("order")
    @classmethod
    def validate_order_field(cls, order: int):
        return validate_order_field(order)


class UpdateSubgroupIncludeCoverChargeItem(BaseModel):
    include_cover_charge: bool
