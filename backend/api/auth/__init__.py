__all__ = ("auth", "login_router")

from fastapi import APIRouter

from .login import login_router

auth = APIRouter(prefix="/auth", tags=["auth"])
auth.include_router(login_router)
