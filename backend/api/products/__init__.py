__all__ = (
    "products",
    "create_product_router",
    "delete_product_router",
    "get_product_router",
    "get_products_router",
    "add_product_date_router",
    "add_product_ingredient_router",
    "add_product_role_router",
    "add_product_variant_router",
)

from fastapi import APIRouter

from .add_product_date import add_product_date_router
from .add_product_ingrendient import add_product_ingredient_router
from .add_product_role import add_product_role_router
from .add_product_variant import add_product_variant_router
from .create_product import create_product_router
from .delete_product import delete_product_router
from .get_product import get_product_router
from .get_products import get_products_router

products = APIRouter(prefix="/products", tags=["products"])
products.include_router(add_product_date_router)
products.include_router(add_product_ingredient_router)
products.include_router(add_product_role_router)
products.include_router(add_product_variant_router)
products.include_router(create_product_router)
products.include_router(delete_product_router)
products.include_router(get_product_router)
products.include_router(get_products_router)
