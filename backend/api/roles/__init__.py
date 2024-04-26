__all__ = (
    "roles",
    "create_role_router",
    "delete_role_router",
    "get_role_router",
    "get_roles_router",
    "update_role_permissions_router",
    "update_role_name_router",
    "update_role_paper_size_router",
)

from fastapi import APIRouter

from .create_role import create_role_router
from .delete_role import delete_role_router
from .get_role import get_role_router
from .get_roles import get_roles_router
from .udpate_role_permissions import update_role_permissions_router
from .update_role_name import update_role_name_router
from .update_role_paper_size import update_role_paper_size_router

roles = APIRouter(prefix="/roles", tags=["roles"])
roles.include_router(create_role_router)
roles.include_router(delete_role_router)
roles.include_router(get_role_router)
roles.include_router(get_roles_router)
roles.include_router(update_role_permissions_router)
roles.include_router(update_role_name_router)
roles.include_router(update_role_paper_size_router)
