from pydantic import BaseModel

from backend.utils import ErrorCodes


class BaseResponse(BaseModel):
    error: bool = False
    code: int = ErrorCodes.SUCCESS.value
    message: str = ""


class UnicornException(Exception):
    def __init__(
        self,
        status: int,
        message: str = "",
        code: ErrorCodes = None,
    ):
        self.status = status
        self.message = message
        self.code = code
