from fastapi import APIRouter, Depends

from backend.config import Session
from backend.database.models import Order
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import BadRequest, Conflict
from backend.models.orders import CreateOrderItem
from backend.utils import Permission, TokenJwt, validate_token
from backend.utils.order_utils import (
    check_menus,
    check_products,
    create_order_menus,
    create_order_products,
)

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
        if not item.products and not item.menus:
            raise BadRequest("NO_PRODUCTS_AND_MENUS")

        if not item.is_take_away and not item.guests:
            raise BadRequest("SET_GUESTS_NUMBER")

        has_error_products, error_code_products, _ = await check_products(
            item.products, token.role_id
        )

        if has_error_products:
            raise Conflict(error_code_products)

        has_error_menus, error_code_menus, _ = await check_menus(
            item.menus, token.role_id
        )

        if has_error_menus:
            raise Conflict(error_code_menus)

        order = await Order.create(
            customer=item.customer,
            guests=item.guests,
            is_take_away=item.is_take_away,
            table=item.table,
            user_id=token.user_id,
        )

        await create_order_products(item.products, order)
        await create_order_menus(item.menus, order)

        return BaseResponse()
