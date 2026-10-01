__all__ = (
    "subgroups",
    "create_subgroup_router",
    "delete_subgroup_router",
    "get_subgroups_router",
    "get_subgroup_router",
    "update_subgroup_include_cover_charge_router",
    "update_subgroup_name_router",
    "update_subgroup_order_router",
)

from fastapi import APIRouter

from .create_subgroup import create_subgroup_router
from .delete_subgroup import delete_subgroup_router
from .get_subgroups import get_subgroups_router
from .get_subgroup import get_subgroup_router
from .update_subgroup_include_cover_charge import update_subgroup_include_cover_charge_router
from .update_subgroup_name import update_subgroup_name_router
from .update_subgroup_order import update_subgroup_order_router

subgroups = APIRouter(prefix="/subgroups", tags=["subgroups"])
subgroups.include_router(create_subgroup_router)
subgroups.include_router(delete_subgroup_router)
subgroups.include_router(get_subgroups_router)
subgroups.include_router(get_subgroup_router)
subgroups.include_router(update_subgroup_include_cover_charge_router)
subgroups.include_router(update_subgroup_name_router)
subgroups.include_router(update_subgroup_order_router)
