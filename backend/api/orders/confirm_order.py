from fastapi import APIRouter, Depends
from tortoise.transactions import in_transaction

from backend.config import Session
from backend.database.models import Order
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import Unauthorized, NotFound
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

confirm_order_router = APIRouter()


@confirm_order_router.patch("/{order_id}/confirm", response_model=BaseResponse)
@check_role(Permission.CAN_CONFIRM_ORDERS)
async def confirm_order(
    order_id: int, token: TokenJwt = Depends(validate_token)
):
    if (
        not Session.settings.order_requires_confirmation
        or not token.permissions["can_confirm_orders"]
    ):
        raise Unauthorized(code=ErrorCodes.NOT_ALLOWED)

    async with in_transaction() as connection:
        updated_count = (
            await Order.filter(id=order_id)
            .using_db(connection)
            .update(is_confirm=True)
        )

        if not updated_count:
            raise NotFound(code=ErrorCodes.ORDER_NOT_FOUND)

    return BaseResponse()
