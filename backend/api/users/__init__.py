__all__ = ("users", "get_user_router", "get_users_router")

from fastapi import APIRouter

from .get_user import get_user_router
from .get_users import get_users_router

users = APIRouter(prefix="/users", tags=["users"])
users.include_router(get_user_router)
users.include_router(get_users_router)
