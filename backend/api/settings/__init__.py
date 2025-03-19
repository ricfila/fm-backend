__all__ = (
    "get_settings_router",
    "update_settings_router",
)

from fastapi import APIRouter

from .get_settings import get_settings_router
from .update_settings import update_settings_router

settings = APIRouter(prefix="/settings", tags=["settings"])
settings.include_router(get_settings_router)
settings.include_router(update_settings_router)
