from pydantic import BaseModel, field_validator

from backend.models import BaseResponse
from backend.models.users import User
from backend.utils import validate_password_field, validate_username_field


class LoginResponse(BaseResponse):
    access_token: str
    token_type: str = "bearer"


class RegisterUserResponse(BaseResponse):
    user: User


class RegisterItem(BaseModel):
    username: str
    password: str
    role_id: int

    @field_validator("username")
    @classmethod
    def validate_username_field(cls, username: str):
        return validate_username_field(username)

    @field_validator("password")
    @classmethod
    def validate_password_field(cls, password: str):
        return validate_password_field(password)
