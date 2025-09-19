from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from backend.database.models import Ingredient, Stock
from backend.decorators import check_role
from backend.models.error import Conflict, NotFound
from backend.models.ingredients import AddStockItem, AddStockResponse
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

add_stock_router = APIRouter()


@add_stock_router.post("/{ingredient_id}/stock", response_model=AddStockResponse)
@check_role(Permission.CAN_ORDER)
async def add_stock(
    ingredient_id: int,
    item: AddStockItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Add a new stock for an ingredient.

    **Permission**: can_order
    """

    async with in_transaction() as connection:
        ingredient = await Ingredient.get_or_none(id=ingredient_id, using_db=connection)
        if not ingredient:
            raise NotFound(code=ErrorCodes.INGREDIENT_NOT_FOUND)
        
        new_stock = Stock(
            ingredient=ingredient,
            quantity=item.quantity,
            is_last_stock=item.is_last_stock
        )

        try:
            await new_stock.save(using_db=connection)

        except IntegrityError:
            raise Conflict(code=ErrorCodes.STOCK_ALREADY_EXISTS)

    return AddStockResponse(stock=await new_stock.to_dict())
