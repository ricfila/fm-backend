from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from backend.database.models import Ingredient
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import Conflict, NotFound
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token
from backend.models.ingredients import UpdateIngredientSellIfStockedItem

update_ingredient_sell_if_stocked_router = APIRouter()


@update_ingredient_sell_if_stocked_router.put("/{ingredient_id}/sell_if_stocked", response_model=BaseResponse)
@check_role(Permission.CAN_ADMINISTER, Permission.CAN_CONFIRM_ORDERS)
async def update_ingredient_sell_if_stocked(
    ingredient_id: int,
    item: UpdateIngredientSellIfStockedItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Update ingredient.

    **Permission**: can_administer, can_confirm_orders
    """

    async with in_transaction() as connection:
        ingredient = await Ingredient.get_or_none(id=ingredient_id, using_db=connection)

        if not ingredient:
            raise NotFound(code=ErrorCodes.INGREDIENT_NOT_FOUND)

        ingredient.sell_if_stocked = item.sell_if_stocked

        try:
            await ingredient.save(using_db=connection)

        except IntegrityError:
            raise Conflict(code=ErrorCodes.INGREDIENT_ALREADY_EXISTS)

    return BaseResponse()
