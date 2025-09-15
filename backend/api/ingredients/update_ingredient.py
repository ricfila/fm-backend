from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from backend.database.models import Ingredient
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import Conflict, NotFound
from backend.models.ingredients import CreateIngredientItem
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

update_ingredient_router = APIRouter()


@update_ingredient_router.put("/{ingredient_id}", response_model=BaseResponse)
@check_role(Permission.CAN_ADMINISTER)
async def update_product_daily_max_sales(
    ingredient_id: int,
    item: CreateIngredientItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Update ingredient.

     **Permission**: can_administer
    """

    async with in_transaction() as connection:
        ingredient = await Ingredient.get_or_none(id=ingredient_id, using_db=connection)

        if not ingredient:
            raise NotFound(code=ErrorCodes.INGREDIENT_NOT_FOUND)

        ingredient.name = item.name
        ingredient.ward = item.ward

        try:
            await ingredient.save(using_db=connection)

        except IntegrityError:
            raise Conflict(code=ErrorCodes.INGREDIENT_ALREADY_EXISTS)

    return BaseResponse()
