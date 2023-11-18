from backend.models import BaseResponse


class LoginResponse(BaseResponse):
    access_token: str
    token_type: str = "bearer"
