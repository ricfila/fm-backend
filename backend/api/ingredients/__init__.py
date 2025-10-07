__all__ = (
    "ingredients",
	"add_stock",
	"create_ingredient",
	"delete_ingredient",
	"delete_stock",
	"get_ingredient",
	"get_ingredients",
	"get_stock_list",
	"get_wards",
	"resume_ingredient",
	"update_ingredient",
	"update_stock"
)

from fastapi import APIRouter

from .get_wards import get_wards_router
from .get_ingredient import get_ingredient_router
from .get_ingredients import get_ingredients_router
from .create_ingredient import create_ingredient_router
from .update_ingredient import update_ingredient_router
from .delete_ingredient import delete_ingredient_router
from .resume_ingredient import resume_ingredient_router
from .add_stock import add_stock_router
from .get_stock_list import get_stock_list_router
from .update_stock import update_stock_router
from .delete_stock import delete_stock_router

ingredients = APIRouter(prefix="/ingredients", tags=["ingredients"])
ingredients.include_router(get_wards_router)
ingredients.include_router(get_ingredient_router)
ingredients.include_router(get_ingredients_router)
ingredients.include_router(create_ingredient_router)
ingredients.include_router(update_ingredient_router)
ingredients.include_router(delete_ingredient_router)
ingredients.include_router(resume_ingredient_router)
ingredients.include_router(add_stock_router)
ingredients.include_router(get_stock_list_router)
ingredients.include_router(update_stock_router)
ingredients.include_router(delete_stock_router)
