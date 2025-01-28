__all__ = (
    "menus",
    "add_menu_date_router",
    "add_menu_field_router",
    "add_menu_field_product_router",
    "add_menu_role_router",
    "create_menu_router",
    "delete_menu_router",
    "delete_menu_date_router",
    "delete_menu_field_router",
    "delete_menu_field_product_router",
    "delete_menu_role_router",
    "get_menu_router",
    "get_menu_products_router",
    "get_menus_router",
    "update_menu_field_additional_cost_router",
    "update_menu_field_is_optional_router",
    "update_menu_field_max_sortable_elements_router",
    "update_menu_field_name_router",
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
from .delete_menu_field import delete_menu_field_router
from .delete_menu_field_product import delete_menu_field_product_router
from .delete_menu_role import delete_menu_role_router
from .get_menu import get_menu_router
from .get_menu_products import get_menu_products_router
from .get_menus import get_menus_router
from .update_menu_field_additional_cost import (
    update_menu_field_additional_cost_router,
)
from .update_menu_field_is_optional import update_menu_field_is_optional_router
from .update_menu_field_max_sortable_elements import (
    update_menu_field_max_sortable_elements_router,
)
from .update_menu_field_name import update_menu_field_name_router
from .update_menu_name import update_menu_name_router
from .update_menu_price import update_menu_price_router
from .update_menu_short_name import update_menu_short_name_router

menus = APIRouter(prefix="/menus", tags=["menu"])
menus.include_router(add_menu_date_router)
menus.include_router(add_menu_field_router)
menus.include_router(add_menu_field_product_router)
menus.include_router(add_menu_role_router)
menus.include_router(create_menu_router)
menus.include_router(delete_menu_router)
menus.include_router(delete_menu_date_router)
menus.include_router(delete_menu_field_router)
menus.include_router(delete_menu_field_product_router)
menus.include_router(delete_menu_role_router)
menus.include_router(get_menu_router)
menus.include_router(get_menu_products_router)
menus.include_router(get_menus_router)
menus.include_router(update_menu_field_additional_cost_router)
menus.include_router(update_menu_field_is_optional_router)
menus.include_router(update_menu_field_max_sortable_elements_router)
menus.include_router(update_menu_field_name_router)
menus.include_router(update_menu_name_router)
menus.include_router(update_menu_price_router)
menus.include_router(update_menu_short_name_router)
