import datetime

from pydantic import BaseModel

from backend.models import BaseResponse


class User(BaseModel):
    id: int
    username: str
    role_id: int
    created_at: datetime.datetime


class GetUsersResponse(BaseResponse):
    users: list[User]


class GetUserResponse(BaseResponse, User):
    pass
