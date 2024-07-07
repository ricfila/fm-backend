__all__ = (
    "orders",
    "create_order_router",
)

from fastapi import APIRouter

from .create_order import create_order_router

orders = APIRouter(prefix="/orders", tags=["orders"])
orders.include_router(create_order_router)
