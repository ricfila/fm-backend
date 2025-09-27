__all__ = (
    "payment_methods",
	"create_payment_method",
	"delete_payment_method",
	"get_payment_method",
	"get_payment_methods",
	"resume_payment_method",
	"update_payment_method"
)

from fastapi import APIRouter

from .get_payment_method import get_payment_method_router
from .get_payment_methods import get_payment_methods_router
from .create_payment_method import create_payment_method_router
from .update_payment_method import update_payment_method_router
from .delete_payment_method import delete_payment_method_router
from .resume_payment_method import resume_payment_method_router

payment_methods = APIRouter(prefix="/payment_methods", tags=["payment_methods"])
payment_methods.include_router(get_payment_method_router)
payment_methods.include_router(get_payment_methods_router)
payment_methods.include_router(create_payment_method_router)
payment_methods.include_router(update_payment_method_router)
payment_methods.include_router(delete_payment_method_router)
payment_methods.include_router(resume_payment_method_router)
