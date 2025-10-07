from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from backend.database.models import Stock
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import Conflict, NotFound
from backend.models.ingredients import UpdateStockItem
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

update_stock_router = APIRouter()


@update_stock_router.put("/{ingredient_id}/stock/{stock_id}", response_model=BaseResponse)
@check_role(Permission.CAN_ORDER)
async def update_stock(
    ingredient_id: int,
    stock_id: int,
    item: UpdateStockItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Update a stock for an ingredient.

    **Permission**: can_order
    """

    async with in_transaction() as connection:
        stock = await Stock.get_or_none(id=stock_id, ingredient_id=ingredient_id, using_db=connection)
        
        if not stock:
            raise NotFound(code=ErrorCodes.STOCK_NOT_FOUND)
        
        if item.quantity is not None:
            stock.quantity = item.quantity
        
        try:
            await stock.save(using_db=connection)
        except IntegrityError:
            raise Conflict(code=ErrorCodes.STOCK_ALREADY_EXISTS)

    return BaseResponse()
