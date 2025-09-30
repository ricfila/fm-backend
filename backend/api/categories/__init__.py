__all__ = (
    "categories",
    "create_category_router",
    "delete_category_router",
    "get_categories_router",
    "get_category_router",
    "update_category_name_router",
    "update_category_parent_category_router",
    "update_category_parent_take_away_router",
    "update_category_parent_main_products_router",
    "update_category_print_delay_router",
    "update_category_printer_router",
)

from fastapi import APIRouter

from .create_category import create_category_router
from .delete_category import delete_category_router
from .get_categories import get_categories_router
from .get_category import get_category_router
from .update_category_name import update_category_name_router
from .update_category_parent_category import update_category_parent_category_router
from .update_category_parent_take_away import update_category_parent_take_away_router
from .update_category_parent_main_products import update_category_parent_main_products_router
from .update_category_print_delay import update_category_print_delay_router
from .update_category_printer import update_category_printer_router

categories = APIRouter(prefix="/categories", tags=["categories"])
categories.include_router(create_category_router)
categories.include_router(delete_category_router)
categories.include_router(get_categories_router)
categories.include_router(get_category_router)
categories.include_router(update_category_name_router)
categories.include_router(update_category_parent_category_router)
categories.include_router(update_category_parent_take_away_router)
categories.include_router(update_category_parent_main_products_router)
categories.include_router(update_category_print_delay_router)
categories.include_router(update_category_printer_router)
