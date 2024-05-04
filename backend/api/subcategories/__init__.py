__all__ = (
    "subcategories",
    "create_subcategory",
    "delete_subcategories_router",
    "get_subcategories_router",
    "get_subcategory_router",
    "update_subcategory_name_router",
    "update_subcategory_order_router",
)

from fastapi import APIRouter

from .create_subcategory import create_subcategory_router
from .delete_subcategory import delete_subcategories_router
from .get_subcategories import get_subcategories_router
from .get_subcategory import get_subcategory_router
from .update_subcategory_name import update_subcategory_name_router
from .update_subcategory_order import update_subcategory_order_router

subcategories = APIRouter(prefix="/subcategories", tags=["subcategories"])
subcategories.include_router(create_subcategory_router)
subcategories.include_router(delete_subcategories_router)
subcategories.include_router(get_subcategories_router)
subcategories.include_router(get_subcategory_router)
subcategories.include_router(update_subcategory_name_router)
subcategories.include_router(update_subcategory_order_router)
