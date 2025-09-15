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
)
from backend.utils import TokenJwt, validate_token, ErrorCodes
from backend.utils.query_utils import process_query_with_pagination

get_ingredients_router = APIRouter()


@get_ingredients_router.get("/", response_model=GetIngredientsResponse)
async def get_ingredients(
    offset: int = 0,
    limit: int | None = None,
    only_name: bool = False,
    order_by: str = None,
    deleted: bool = False,
    token: TokenJwt = Depends(validate_token),
):
    """
    Get list of ingredients.
    """

    async with in_transaction() as connection:
        (
            ingredient_query,
            total_count,
            limit,
        ) = await process_query_with_pagination(
            Ingredient, Q(is_deleted=deleted), connection, offset, limit, order_by
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
