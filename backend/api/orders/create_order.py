from fastapi import APIRouter, Depends

from backend.config import Session
from backend.database.models import Order
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import Conflict
from backend.models.orders import CreateOrderItem
from backend.utils import Permission, TokenJwt, validate_token
from backend.utils.order_utils import check_products, create_order_products

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

    async with Session.lock:
        # TODO: check input order

        has_error, error_code, _ = await check_products(
            item.products, token.role_id
        )

        if has_error:
            raise Conflict(error_code)

        order = await Order.create(
            customer=item.customer,
            guests=item.guests,
            is_take_away=item.is_take_away,
            table=item.table,
            user_id=token.user_id,
        )

        await create_order_products(item.products, order)

        return BaseResponse()
