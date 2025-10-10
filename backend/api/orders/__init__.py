__all__ = (
    "orders",
	"confirm_order_router",
	"confirm_orders_router",
    "create_order_router",
    "update_order_router",
    "delete_order_router",
    "resume_order_router",
    "get_order_router",
    "get_orders_router",
    "print_order_router",
	"get_tickets_router",
	"update_tickets_router",
    "delete_tickets_router",
)

from fastapi import APIRouter

from .confirm_order import confirm_order_router
from .confirm_orders import confirm_orders_router
from .create_order import create_order_router
from .update_order import update_order_router
from .delete_order import delete_order_router
from .resume_order import resume_order_router
from .get_order import get_order_router
from .get_orders import get_orders_router
from .print_order import print_order_router
from .get_tickets import get_tickets_router
from .update_tickets import update_tickets_router
from .delete_tickets import delete_tickets_router

orders = APIRouter(prefix="/orders", tags=["orders"])
orders.include_router(confirm_order_router)
orders.include_router(confirm_orders_router)
orders.include_router(create_order_router)
orders.include_router(update_order_router)
orders.include_router(delete_order_router)
orders.include_router(resume_order_router)
orders.include_router(get_order_router)
orders.include_router(get_orders_router)
orders.include_router(print_order_router)
orders.include_router(get_tickets_router)
orders.include_router(update_tickets_router)
orders.include_router(delete_tickets_router)
