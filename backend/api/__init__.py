__all__ = ("api", "auth", "roles", "users")

from fastapi import APIRouter

from .auth import auth
from .roles import roles
from .users import users

api = APIRouter()
api.include_router(auth)
api.include_router(roles)
api.include_router(users)
