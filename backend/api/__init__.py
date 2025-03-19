__all__ = (
    "api",
    "auth",
    "menus",
    "orders",
    "products",
    "roles",
    "settings",
    "subcategories",
    "users",
)

from fastapi import APIRouter

from .auth import auth
from .menus import menus
from .orders import orders
from .products import products
from .roles import roles
from .settings import settings
from .subcategories import subcategories
from .users import users

api = APIRouter()
api.include_router(auth)
api.include_router(menus)
api.include_router(orders)
api.include_router(products)
api.include_router(roles)
api.include_router(settings)
api.include_router(subcategories)
api.include_router(users)
