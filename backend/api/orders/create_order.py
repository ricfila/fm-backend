from fastapi import APIRouter, Depends

from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.orders import CreateOrderItem
from backend.utils import Permission, TokenJwt, validate_token

create_order_router = APIRouter()


@create_order_router.post("/", response_model=BaseResponse)
@check_role(Permission.CAN_ORDER)
async def create_order(
    item: CreateOrderItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Create a new order.

    **Permission**: can_order
    """

    pass
