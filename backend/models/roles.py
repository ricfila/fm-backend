from pydantic import BaseModel, field_validator

from backend.models import BaseResponse
from backend.utils import PaperSize, Permission


class Role(BaseModel):
    id: int
    name: str


class GetRolesResponse(BaseResponse):
    total_count: int
    roles: list[Role]


class GetRoleResponse(BaseResponse):
    id: int
    name: str
    permissions: dict[Permission, bool]
    paper_size: PaperSize | None


class CreateRoleItem(BaseModel):
    name: str
    permissions: dict[Permission, bool] = dict()
    paper_size: PaperSize | None = None

    @field_validator("name")
    @classmethod
    def validate_name_field(cls, name: str):
        return _validate_name_field(name)

    @field_validator("permissions")
    @classmethod
    def validate_permissions_field(cls, permissions: dict[Permission, bool]):
        return _validate_permissions_field(permissions)


class UpdateRoleNameItem(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def validate_name_field(cls, name: str):
        return _validate_name_field(name)


class UpdateRolePermissionsItem(BaseModel):
    permissions: dict[Permission, bool]

    @field_validator("permissions")
    @classmethod
    def validate_permissions_field(cls, permissions: dict[Permission, bool]):
        return _validate_permissions_field(permissions)


class UpdateRolePaperSizeItem(BaseModel):
    paper_size: PaperSize


def _validate_name_field(name: str):
    if not name:
        raise ValueError("The `name` field can not be empty")

    if len(name) > 32:
        raise ValueError(
            "The `name` field must have a maximum length of 32 characters"
        )

    return name


def _validate_permissions_field(permissions: dict[Permission, bool]):
    if Permission.CAN_ADMINISTER in permissions:
        raise ValueError("The `permissions` field can't be administrators")

    return permissions
