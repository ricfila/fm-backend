__all__ = (
    "menu",
    "add_menu_date_router",
    "add_menu_field_router",
    "add_menu_field_product_router",
    "add_menu_role_router",
    "create_menu_router",
    "delete_menu_router",
    "delete_menu_date_router",
    "delete_menu_role_router",
    "get_menu_router",
    "get_menus_router",
    "update_menu_name_router",
    "update_menu_price_router",
    "update_menu_short_name_router",
)

from fastapi import APIRouter

from .add_menu_date import add_menu_date_router
from .add_menu_field import add_menu_field_router
from .add_menu_field_product import add_menu_field_product_router
from .add_menu_role import add_menu_role_router
from .create_menu import create_menu_router
from .delete_menu import delete_menu_router
from .delete_menu_date import delete_menu_date_router
from .delete_menu_role import delete_menu_role_router
from .get_menu import get_menu_router
from .get_menus import get_menus_router
from .update_menu_name import update_menu_name_router
from .update_menu_price import update_menu_price_router
from .update_menu_short_name import update_menu_short_name_router

menu = APIRouter(prefix="/menu", tags=["menu"])
menu.include_router(add_menu_date_router)
menu.include_router(add_menu_field_router)
menu.include_router(add_menu_field_product_router)
menu.include_router(add_menu_role_router)
menu.include_router(create_menu_router)
menu.include_router(delete_menu_router)
menu.include_router(delete_menu_date_router)
menu.include_router(delete_menu_role_router)
menu.include_router(get_menu_router)
menu.include_router(get_menus_router)
menu.include_router(update_menu_name_router)
menu.include_router(update_menu_price_router)
menu.include_router(update_menu_short_name_router)
