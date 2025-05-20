__all__ = (
    "products",
    "add_product_date_router",
    "add_product_ingredient_router",
    "add_product_role_router",
    "add_product_variant_router",
    "create_product_router",
    "delete_product_router",
    "delete_product_date_router",
    "delete_product_ingredient_router",
    "delete_product_role_router",
    "delete_product_variant_router",
    "get_product_router",
    "get_products_router",
    "update_product_category_router",
    "update_product_daily_max_sales_router",
    "update_product_is_priority_router",
    "update_product_name_router",
    "update_product_order_router",
    "update_product_price_router",
    "update_product_short_name_router",
    "update_product_subcategory_router",
)

from fastapi import APIRouter

from .add_product_date import add_product_date_router
from .add_product_ingrendient import add_product_ingredient_router
from .add_product_role import add_product_role_router
from .add_product_variant import add_product_variant_router
from .create_product import create_product_router
from .delete_product import delete_product_router
from .delete_product_date import delete_product_date_router
from .delete_product_ingredient import delete_product_ingredient_router
from .delete_product_role import delete_product_role_router
from .delete_product_variant import delete_product_variant_router
from .get_product import get_product_router
from .get_products import get_products_router
from .update_product_category import update_product_category_router
from .update_product_daily_max_sales import (
    update_product_daily_max_sales_router,
)
from .update_product_is_priority import update_product_is_priority_router
from .update_product_name import update_product_name_router
from .update_product_order import update_product_order_router
from .update_product_price import update_product_price_router
from .update_product_short_name import update_product_short_name_router
from .update_product_subcategory import update_product_subcategory_router

products = APIRouter(prefix="/products", tags=["products"])
products.include_router(add_product_date_router)
products.include_router(add_product_ingredient_router)
products.include_router(add_product_role_router)
products.include_router(add_product_variant_router)
products.include_router(create_product_router)
products.include_router(delete_product_router)
products.include_router(delete_product_date_router)
products.include_router(delete_product_ingredient_router)
products.include_router(delete_product_role_router)
products.include_router(delete_product_variant_router)
products.include_router(get_product_router)
products.include_router(get_products_router)
products.include_router(update_product_category_router)
products.include_router(update_product_daily_max_sales_router)
products.include_router(update_product_is_priority_router)
products.include_router(update_product_name_router)
products.include_router(update_product_order_router)
products.include_router(update_product_price_router)
products.include_router(update_product_short_name_router)
products.include_router(update_product_subcategory_router)
