from pydantic import BaseModel


class BaseResponse(BaseModel):
    error: bool = False
    message: str = ""


class UnicornException(Exception):
    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message
