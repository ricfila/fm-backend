from pydantic import BaseModel, field_validator

from backend.models import BaseResponse
from backend.utils import validate_name_field, validate_order_field


class Group(BaseModel):
    id: int
    name: str
    order: int


class CreateGroupItem(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def validate_name_field(cls, name: str):
        return validate_name_field(name)


class CreateGroupResponse(BaseResponse):
    group: Group


class GetGroupsResponse(BaseResponse):
    total_count: int
    groups: list[Group]


class GetGroupResponse(BaseResponse, Group):
    pass


class UpdateGroupNameItem(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def validate_name_field(cls, name: str):
        return validate_name_field(name)


class UpdateGroupOrderItem(BaseModel):
    order: int

    @field_validator("order")
    @classmethod
    def validate_order_field(cls, order: int):
        return validate_order_field(order)
