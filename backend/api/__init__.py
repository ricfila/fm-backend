__all__ = (
    "api",
    "auth",
	"categories",
	"ingredients",
    "menus",
    "orders",
	"payment_methods",
    "printers",
    "products",
    "roles",
    "settings",
    "statistics",
    "subcategories",
	"tickets",
    "users",
)

from fastapi import APIRouter

from .auth import auth
from .categories import categories
from .ingredients import ingredients
from .menus import menus
from .orders import orders
from .payment_methods import payment_methods
from .printers import printers
from .products import products
from .roles import roles
from .settings import settings
from .statistics import statistics
from .subcategories import subcategories
from .tickets import tickets
from .users import users

api = APIRouter()
api.include_router(auth)
api.include_router(categories)
api.include_router(ingredients)
api.include_router(menus)
api.include_router(orders)
api.include_router(payment_methods)
api.include_router(printers)
api.include_router(products)
api.include_router(roles)
api.include_router(settings)
api.include_router(statistics)
api.include_router(subcategories)
api.include_router(tickets)
api.include_router(users)
