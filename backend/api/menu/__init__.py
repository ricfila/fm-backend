__all__ = (
    "menu",
    "create_menu_router",
    "delete_menu_router",
    "get_menu_router",
    "get_menus_router",
)

from fastapi import APIRouter

from .create_menu import create_menu_router
from .delete_menu import delete_menu_router
from .get_menu import get_menu_router
from .get_menus import get_menus_router

menu = APIRouter(prefix="/menu", tags=["menu"])
menu.include_router(create_menu_router)
menu.include_router(delete_menu_router)
menu.include_router(get_menu_router)
menu.include_router(get_menus_router)
