from fastapi import APIRouter, Depends
from tortoise.transactions import in_transaction

from backend.config import Session
from backend.database.models import Order
from backend.decorators import check_role
from backend.models.error import NotFound
from backend.models import BaseResponse
from backend.models.orders import PrintOrderItem
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

print_order_router = APIRouter()


@print_order_router.post("/{order_id}/print", response_model=BaseResponse)
@check_role(Permission.CAN_ADMINISTER)
async def print_order(
    order_id: int,
    item: PrintOrderItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Print order.

    **Permission**: can_administer
    """

    async with in_transaction() as connection:
        order = (
            await Order.filter(id=order_id)
            .prefetch_related(
                "order_menus__order_menu_fields__order_menu_field_products__order_product_ingredients__product_ingredient",
                "order_menus__menu",
                "order_products__order_product_ingredients__product_ingredient",
                "order_products__variant",
                "user__role__printers__printer",
                "user__role__order_confirmer__printers__printer",
                "order_printers__role_printer__printer",
                "confirmed_by__role__printers__printer",
            )
            .using_db(connection)
            .first()
        )

        if not order:
            raise NotFound(code=ErrorCodes.ORDER_NOT_FOUND)

    await Session.print_manager.add_job(order, item.printer_types)

    return BaseResponse()
