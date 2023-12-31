from pydantic import BaseModel, field_validator

from backend.models import BaseResponse


class User(BaseModel):
    id: int
    username: str
    role_id: int


class GetUsersResponse(BaseResponse):
    users: list[User]
