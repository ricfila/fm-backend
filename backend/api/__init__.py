__all__ = ("api", "auth", "roles", "subcategories", "users")

from fastapi import APIRouter

from .auth import auth
from .roles import roles
from .subcategories import subcategories
from .users import users

api = APIRouter()
api.include_router(auth)
api.include_router(roles)
api.include_router(subcategories)
api.include_router(users)
