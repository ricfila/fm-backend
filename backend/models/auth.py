from pydantic import BaseModel, field_validator

from backend.models import BaseResponse


class LoginResponse(BaseResponse):
    access_token: str
    token_type: str = "bearer"


class RegisterItem(BaseModel):
    username: str
    password: str
    role_id: int

    @field_validator("username")
    @classmethod
    def validate_username_field(cls, username: str):
        if not username:
            raise ValueError("The `username` field can not be empty")

        if len(username) > 32:
            raise ValueError(
                "The `username` field must have a maximum length of 32 characters"
            )

        if not username.isalpha():
            raise ValueError("The `username` field has illegal characters")

        return username

    @field_validator("password")
    @classmethod
    def validate_password_field(cls, password: str):
        if not password:
            raise ValueError("The `password` field can not be empty")

        if len(password) > 32:
            raise ValueError(
                "The `password` field must have a maximum length of 32 characters"
            )

        return password
