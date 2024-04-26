from pydantic import BaseModel, field_validator

from backend.models import BaseResponse
from backend.utils import (
    PaperSize,
    Permission,
    validate_name_field,
    validate_permissions_field,
)


class Role(BaseModel):
    id: int
    name: str
    permissions: dict[Permission, bool]
    paper_size: PaperSize | None


class GetRolesResponse(BaseResponse):
    total_count: int
    roles: list[Role]


class GetRoleResponse(BaseResponse, Role):
    pass


class CreateRoleItem(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def validate_name_field(cls, name: str):
        return validate_name_field(name)


class UpdateRoleNameItem(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def validate_name_field(cls, name: str):
        return validate_name_field(name)


class UpdateRolePermissionsItem(BaseModel):
    permissions: dict[Permission, bool]

    @field_validator("permissions")
    @classmethod
    def validate_permissions_field(cls, permissions: dict[Permission, bool]):
        return validate_permissions_field(permissions)


class UpdateRolePaperSizeItem(BaseModel):
    paper_size: PaperSize
