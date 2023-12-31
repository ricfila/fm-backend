__all__ = ("users", "get_users_router")

from fastapi import APIRouter

from .get_users import get_users_router

users = APIRouter(prefix="/users", tags=["users"])
users.include_router(get_users_router)
