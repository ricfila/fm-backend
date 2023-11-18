__all__ = ("auth", "login_router", "register_router")

from fastapi import APIRouter

from .login import login_router
from .register import register_router

auth = APIRouter(prefix="/auth", tags=["auth"])
auth.include_router(login_router)
auth.include_router(register_router)
