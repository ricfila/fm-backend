__all__ = (
    "create_printer_router",
    "delete_printer_router",
    "get_printer_router",
    "get_printers_router",
    "update_printer_ip_address_router",
    "update_printer_name_router",
)

from fastapi import APIRouter

from .create_printer import create_printer_router
from .delete_printer import delete_printer_router
from .get_printer import get_printer_router
from .get_printers import get_printers_router
from .update_printer_ip_address import update_printer_ip_address_router
from .update_printer_name import update_printer_name_router

printers = APIRouter(prefix="/printers", tags=["printers"])
printers.include_router(create_printer_router)
printers.include_router(delete_printer_router)
printers.include_router(get_printer_router)
printers.include_router(get_printers_router)
printers.include_router(update_printer_ip_address_router)
printers.include_router(update_printer_name_router)
