__all__ = ("api", "auth", "users")

from fastapi import APIRouter

from .auth import auth
from .users import users

api = APIRouter()
api.include_router(auth)
api.include_router(users)
