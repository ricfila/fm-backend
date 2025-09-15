from fastapi import APIRouter, Depends
from tortoise.transactions import in_transaction

from backend.database.models import Ingredient
from backend.models.error import NotFound
from backend.models.ingredients import GetIngredientResponse
from backend.utils import ErrorCodes, TokenJwt, validate_token

get_ingredient_router = APIRouter()


@get_ingredient_router.get("/{ingredient_id}", response_model=GetIngredientResponse)
async def get_ingredient(
    ingredient_id: int, token: TokenJwt = Depends(validate_token)
):
    """
    Get information about an ingredient.
    """

    async with in_transaction() as connection:
        ingredient = await Ingredient.get_or_none(id=ingredient_id, using_db=connection)

        if not ingredient:
            raise NotFound(code=ErrorCodes.INGREDIENT_NOT_FOUND)

    return GetIngredientResponse(**await ingredient.to_dict())
