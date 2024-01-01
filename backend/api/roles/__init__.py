__all__ = ("roles", "create_role_router")

from fastapi import APIRouter

from .create_role import create_role_router

roles = APIRouter(prefix="/roles", tags=["roles"])
roles.include_router(create_role_router)
