from pydantic import BaseModel, field_validator

from backend.models import BaseResponse
from backend.utils import PaperSize, Permission


class Role(BaseModel):
    id: int
    name: str


class GetRolesResponse(BaseResponse):
    roles: list[Role]


class CreateRoleItem(BaseModel):
    name: str
    permissions: dict[Permission, bool] = dict()
    paper_size: PaperSize | None = None

    @field_validator("name")
    @classmethod
    def validate_name_field(cls, name: str):
        if not name:
            raise ValueError("The `name` field can not be empty")

        if len(name) > 32:
            raise ValueError(
                "The `name` field must have a maximum length of 32 characters"
            )

        return name

    @field_validator("permissions")
    @classmethod
    def validate_permissions_field(cls, permissions: dict[Permission, bool]):
        if Permission.CAN_ADMINISTER in permissions:
            raise ValueError("The `permissions` field can't be administrators")

        return permissions
