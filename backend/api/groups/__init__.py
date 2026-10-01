__all__ = (
    "groups",
    "create_group_router",
    "delete_group_router",
    "get_groups_router",
    "get_group_router",
    "update_group_include_cover_charge_router",
    "update_group_name_router",
    "update_group_order_router",
)

from fastapi import APIRouter

from .create_group import create_group_router
from .delete_group import delete_group_router
from .get_groups import get_groups_router
from .get_group import get_group_router
from .update_group_name import update_group_name_router
from .update_group_order import update_group_order_router

groups = APIRouter(prefix="/groups", tags=["groups"])
groups.include_router(create_group_router)
groups.include_router(delete_group_router)
groups.include_router(get_groups_router)
groups.include_router(get_group_router)
groups.include_router(update_group_name_router)
groups.include_router(update_group_order_router)
