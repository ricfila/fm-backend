__all__ = (
    "orders",
    "create_order_router",
    "delete_order_router",
    "get_order_router",
    "get_orders_router",
)

from fastapi import APIRouter

from .create_order import create_order_router
from .delete_order import delete_order_router
from .get_order import get_order_router
from .get_orders import get_orders_router

orders = APIRouter(prefix="/orders", tags=["orders"])
orders.include_router(create_order_router)
orders.include_router(delete_order_router)
orders.include_router(get_order_router)
orders.include_router(get_orders_router)
