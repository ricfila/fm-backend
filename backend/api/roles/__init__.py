__all__ = ("roles", "create_role_router", "get_roles_router")

from fastapi import APIRouter

from .create_role import create_role_router
from .get_roles import get_roles_router

roles = APIRouter(prefix="/roles", tags=["roles"])
roles.include_router(create_role_router)
roles.include_router(get_roles_router)
