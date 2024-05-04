__all__ = (
    "products",
    "create_product_router",
    "delete_product_router",
    "get_product_router",
    "get_products_router",
)

from fastapi import APIRouter

from .create_product import create_product_router
from .delete_product import delete_product_router
from .get_product import get_product_router
from .get_products import get_products_router

products = APIRouter(prefix="/products", tags=["products"])
products.include_router(create_product_router)
products.include_router(delete_product_router)
products.include_router(get_product_router)
products.include_router(get_products_router)
