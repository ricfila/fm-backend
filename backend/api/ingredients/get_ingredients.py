from fastapi import APIRouter, Depends
from tortoise.exceptions import ParamsError
from tortoise.expressions import Q
from tortoise.transactions import in_transaction

from backend.database.models import Ingredient
from backend.models.error import BadRequest
from backend.models.ingredients import (
    GetIngredientsResponse,
    Ingredient as IngredientModel,
    IngredientName,
    IngredientStock,
    IngredientQuantities
)
from backend.utils import TokenJwt, validate_token, ErrorCodes
from backend.utils.query_utils import process_query_with_pagination
from backend.services.ingredients import get_ingredient_stock, get_ingredients_completed_quantities

get_ingredients_router = APIRouter()


@get_ingredients_router.get("/", response_model=GetIngredientsResponse)
async def get_ingredients(
    offset: int = 0,
    limit: int | None = None,
    only_name: bool = False,
    order_by: str = None,
    ward: str = None,
    deleted: bool = False,
    include_stock_quantities: bool = False,
    include_completed_quantities: bool = False,
    await_cooking_time: bool = False,
    token: TokenJwt = Depends(validate_token),
):
    """
    Get list of ingredients.
    """

    async with in_transaction() as connection:
        if include_stock_quantities:
            ingredients = await get_ingredient_stock(connection, ward=ward, await_cooking_time=await_cooking_time)

            return GetIngredientsResponse(
                total_count=len(ingredients),
                ingredients=[
                    IngredientStock(**ingredient)
                    for ingredient in ingredients
                ]
            )
        
        elif include_completed_quantities:
            ingredients = await get_ingredients_completed_quantities(connection, ward=ward, only_monitored=True)

            return GetIngredientsResponse(
                total_count=len(ingredients),
                ingredients=[
                    IngredientQuantities(**ingredient)
                    for ingredient in ingredients
                ]
            )
        
        else:
            query = Q(is_deleted=deleted)

            if ward is not None:
                query &= Q(ward=ward)
            
            (
                ingredient_query,
                total_count,
                limit,
            ) = await process_query_with_pagination(
                Ingredient, query, connection, offset, limit, order_by
            )

            try:
                ingredients = await ingredient_query.offset(offset).limit(limit)
            except ParamsError:
                raise BadRequest(code=ErrorCodes.INVALID_OFFSET_OR_LIMIT_NEGATIVE)

            return GetIngredientsResponse(
                total_count=total_count,
                ingredients=[
                    IngredientName(**await ingredient.to_dict_name())
                    if only_name
                    else IngredientModel(**await ingredient.to_dict())
                    for ingredient in ingredients
                ],
            )
