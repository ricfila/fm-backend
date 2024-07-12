from typing import Any

from fastapi import status

from backend.models import UnicornException
from backend.utils import ErrorCodes


class BadRequest(UnicornException):
    def __init__(
        self,
        message: str = "",
        code: ErrorCodes = None,
        details: dict[str, Any] = None,
    ):
        super().__init__(status.HTTP_400_BAD_REQUEST, message, code, details)


class Unauthorized(UnicornException):
    def __init__(
        self,
        message: str = "",
        code: ErrorCodes = None,
        details: dict[str, Any] = None,
    ):
        super().__init__(status.HTTP_401_UNAUTHORIZED, message, code, details)


class Forbidden(UnicornException):
    def __init__(
        self,
        message: str = "",
        code: ErrorCodes = None,
        details: dict[str, Any] = None,
    ):
        super().__init__(status.HTTP_403_FORBIDDEN, message, code, details)


class NotFound(UnicornException):
    def __init__(
        self,
        message: str = "",
        code: ErrorCodes = None,
        details: dict[str, Any] = None,
    ):
        super().__init__(status.HTTP_404_NOT_FOUND, message, code, details)


class Conflict(UnicornException):
    def __init__(
        self,
        message: str = "",
        code: ErrorCodes = None,
        details: dict[str, Any] = None,
    ):
        super().__init__(status.HTTP_409_CONFLICT, message, code, details)
