__all__ = (
    "api",
    "auth",
    "menu",
    "products",
    "roles",
    "subcategories",
    "users",
)

from fastapi import APIRouter

from .auth import auth
from .menu import menu
from .products import products
from .roles import roles
from .subcategories import subcategories
from .users import users

api = APIRouter()
api.include_router(auth)
api.include_router(menu)
api.include_router(products)
api.include_router(roles)
api.include_router(subcategories)
api.include_router(users)
