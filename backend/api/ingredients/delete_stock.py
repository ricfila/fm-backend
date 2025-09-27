from fastapi import APIRouter, Depends
from tortoise.transactions import in_transaction

from backend.database.models import Stock
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import NotFound
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

delete_stock_router = APIRouter()


@delete_stock_router.delete("/{ingredient_id}/stock/{stock_id}", response_model=BaseResponse)
@check_role(Permission.CAN_ORDER)
async def delete_stock(
    ingredient_id: int,
    stock_id: int,
    token: TokenJwt = Depends(validate_token),
):
    """
    Delete a stock for an ingredient.

    **Permission**: can_order
    """

    async with in_transaction() as connection:
        stock = await Stock.get_or_none(id=stock_id, ingredient_id=ingredient_id, using_db=connection)
        
        if not stock:
            raise NotFound(code=ErrorCodes.STOCK_NOT_FOUND)

        await stock.delete(using_db=connection)

    return BaseResponse()
