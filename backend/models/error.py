from fastapi import status

from backend.models import UnicornException


class BadRequest(UnicornException):
    def __init__(self, message: str):
        super().__init__(status.HTTP_400_BAD_REQUEST, message)


class Unauthorized(UnicornException):
    def __init__(self, message: str):
        super().__init__(status.HTTP_401_UNAUTHORIZED, message)


class Forbidden(UnicornException):
    def __init__(self, message: str):
        super().__init__(status.HTTP_403_FORBIDDEN, message)


class NotFound(UnicornException):
    def __init__(self, message: str):
        super().__init__(status.HTTP_404_NOT_FOUND, message)


class Conflict(UnicornException):
    def __init__(self, message: str):
        super().__init__(status.HTTP_409_CONFLICT, message)
