from typing import Any

from pydantic import BaseModel

from backend.utils import ErrorCodes


class BaseResponseError(BaseModel):
    code: int
    details: dict[str, Any]


class BaseResponse(BaseModel):
    error: bool | BaseResponseError = False
    message: str = ""


class UnicornException(Exception):
    def __init__(
        self,
        status: int,
        message: str = "",
        code: ErrorCodes = None,
        details: dict[str, Any] = None,
    ):
        self.status = status
        self.message = message
        self.code = code
        self.details = details or dict()
