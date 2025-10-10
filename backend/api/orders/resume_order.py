from fastapi import APIRouter, Depends
from tortoise.transactions import in_transaction

from backend.database.models import Order
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import NotFound
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

resume_order_router = APIRouter()


@resume_order_router.post("/{order_id}")
@check_role(Permission.CAN_ADMINISTER, Permission.CAN_ORDER)
async def resume_order(
    order_id: int, token: TokenJwt = Depends(validate_token)
):
    """
    Resume an order from the id.

    **Permission**: can_administer, can_order
    """

    async with in_transaction() as connection:
        order = await Order.get_or_none(id=order_id, using_db=connection)

        if not order:
            raise NotFound(code=ErrorCodes.ORDER_NOT_FOUND)

        order.is_deleted = False
        await order.save(using_db=connection)

    return BaseResponse()
