from fastapi import status

from backend.models import UnicornException
from backend.utils import ErrorCodes


class BadRequest(UnicornException):
    def __init__(
        self,
        message: str = "",
        code: ErrorCodes = None,
    ):
        super().__init__(status.HTTP_400_BAD_REQUEST, message, code)


class Unauthorized(UnicornException):
    def __init__(
        self,
        message: str = "",
        code: ErrorCodes = None,
    ):
        super().__init__(status.HTTP_401_UNAUTHORIZED, message, code)


class Forbidden(UnicornException):
    def __init__(
        self,
        message: str = "",
        code: ErrorCodes = None,
    ):
        super().__init__(status.HTTP_403_FORBIDDEN, message, code)


class NotFound(UnicornException):
    def __init__(
        self,
        message: str = "",
        code: ErrorCodes = None,
    ):
        super().__init__(status.HTTP_404_NOT_FOUND, message, code)


class Conflict(UnicornException):
    def __init__(
        self,
        message: str = "",
        code: ErrorCodes = None,
    ):
        super().__init__(status.HTTP_409_CONFLICT, message, code)
