from fastapi import APIRouter, Depends
from tortoise.expressions import Q
from tortoise.transactions import in_transaction

from backend.database.models import Stock
from backend.decorators import check_role
from backend.models.error import NotFound
from backend.models.ingredients import Stock as StockModel, StockListResponse
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

get_stock_list_router = APIRouter()


@get_stock_list_router.get("/{ingredient_id}/stock", response_model=StockListResponse)
@check_role(Permission.CAN_CONFIRM_ORDERS)
async def get_stock_list(
    ingredient_id: int,
    from_date: str = None,
    to_date: str = None,
    valid: bool = True,
    token: TokenJwt = Depends(validate_token),
):
    """
    Get the stock list for an ingredient.

    **Permission**: can_confirm_orders
    """

    async with in_transaction() as connection:
        query = Q(available_from__gte=from_date) if from_date is not None else Q()
        query &= Q(available_to__lte=to_date) if to_date is not None else Q()

        stocks = await Stock.filter(
            query,
            ingredient_id=ingredient_id,
            is_valid=valid
        ).using_db(connection).order_by('available_from').all()
        
        if not stocks:
            raise NotFound(code=ErrorCodes.STOCK_NOT_FOUND)
        
        total_quantity = sum([stock.quantity for stock in stocks])

    return StockListResponse(
        total_quantity=total_quantity,
        stocks=[
            StockModel(**await stock.to_dict())
            for stock in stocks
        ]
    )
