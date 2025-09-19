from fastapi import APIRouter, Depends
from tortoise.expressions import Q
from tortoise.transactions import in_transaction

from backend.database.models import Stock
from backend.decorators import check_role
from backend.models.error import NotFound
from backend.models.ingredients import StockListResponse
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

get_stock_list_router = APIRouter()


@get_stock_list_router.get("/{ingredient_id}/stock", response_model=StockListResponse)
@check_role(Permission.CAN_ORDER)
async def get_stock_list(
    ingredient_id: int,
    from_date: str = None,
    to_date: str = None,
    last_stock: bool = False,
    token: TokenJwt = Depends(validate_token),
):
    """
    Get the stock list for an ingredient.

    **Permission**: can_order
    """

    async with in_transaction() as connection:
        query = Q(available_from__gte=from_date) if from_date else Q()
        query &= Q(available_to__lte=to_date) if to_date else Q()

        stocks = await Stock.filter(
            query,
            ingredient_id=ingredient_id,
            last_stock=last_stock,
            order_by=Stock.available_from
        ).using_db(connection).all()
        
        if not stocks:
            raise NotFound(code=ErrorCodes.STOCK_NOT_FOUND)
        
        total_quantity = sum([stock.quantity for stock in stocks])

    return StockListResponse(
        total_quantity=total_quantity,
        stocks=await [Stock(**stock.dict()) for stock in stocks]
    )
