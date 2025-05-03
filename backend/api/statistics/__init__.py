__all__ = ("get_statistic_router",)

from fastapi import APIRouter

from .get_statistic import get_statistic_router

statistics = APIRouter(prefix="/statistics", tags=["statistics"])
statistics.include_router(get_statistic_router)
