import datetime

from pydantic import BaseModel, field_validator

from backend.models import BaseResponse
from backend.utils import validate_password_field, validate_username_field


class User(BaseModel):
    id: int
    username: str
    role_id: int
    created_at: datetime.datetime


class GetUsersResponse(BaseResponse):
    total_count: int
    users: list[User]


class GetUserResponse(BaseResponse, User):
    pass


class UpdateUserNameItem(BaseModel):
    username: str

    @field_validator("username")
    @classmethod
    def validate_username_field(cls, username: str):
        return validate_username_field(username)


class UpdateUserPasswordItem(BaseModel):
    password: str

    @field_validator("password")
    @classmethod
    def validate_password_field(cls, password: str):
        return validate_password_field(password)
