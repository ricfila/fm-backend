from fastapi import APIRouter, Depends
from tortoise.transactions import in_transaction

from backend.database.models import Ingredient
from backend.models.error import NotFound
from backend.models.ingredients import GetIngredientResponse, GetIngredientStockResponse
from backend.utils import ErrorCodes, TokenJwt, validate_token
from backend.services.ingredients import get_ingredient_stock

get_ingredient_router = APIRouter()


@get_ingredient_router.get("/{ingredient_id}", response_model=GetIngredientStockResponse)
async def get_ingredient(
    ingredient_id: int,
    include_stock_quantities: bool = False,
    await_cooking_time: bool = False,
    token: TokenJwt = Depends(validate_token)
):
    """
    Get information about an ingredient.
    """

    async with in_transaction() as connection:
        if include_stock_quantities:
            ingredient = (await get_ingredient_stock(
                connection,
                ingredient_id=ingredient_id,
                await_cooking_time=await_cooking_time
            ))[0]

            return GetIngredientStockResponse(ingredient)
        else:
            ingredient = await Ingredient.get_or_none(id=ingredient_id, using_db=connection)

            if not ingredient:
                raise NotFound(code=ErrorCodes.INGREDIENT_NOT_FOUND)

            return GetIngredientResponse(**await ingredient.to_dict())
