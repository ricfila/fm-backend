__all__ = (
    "ingredients",
	"create_ingredient",
	"delete_ingredient",
	"get_ingredient",
	"get_ingredients",
	"resume_ingredient",
	"update_ingredient"
)

from fastapi import APIRouter

from .get_ingredient import get_ingredient_router
from .get_ingredients import get_ingredients_router
from .create_ingredient import create_ingredient_router
from .update_ingredient import update_ingredient_router
from .delete_ingredient import delete_ingredient_router
from .resume_ingredient import resume_ingredient_router

ingredients = APIRouter(prefix="/ingredients", tags=["ingredients"])
ingredients.include_router(get_ingredient_router)
ingredients.include_router(get_ingredients_router)
ingredients.include_router(create_ingredient_router)
ingredients.include_router(update_ingredient_router)
ingredients.include_router(delete_ingredient_router)
ingredients.include_router(resume_ingredient_router)
