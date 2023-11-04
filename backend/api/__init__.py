__all__ = ("api", "auth")

from fastapi import APIRouter

from .auth import auth

api = APIRouter()
api.include_router(auth)
