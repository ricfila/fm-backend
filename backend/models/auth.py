from backend.models import BaseResponse


class LoginResponse(BaseResponse):
    token: str
