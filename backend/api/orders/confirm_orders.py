import datetime
import pytz

from fastapi import APIRouter, Depends
from tortoise.transactions import in_transaction

from backend.config import Session
from backend.database.models import Order
from backend.decorators import check_role
from backend.models.error import Unauthorized
from backend.models.orders import ConfirmOrdersItem, ConfirmOrdersResponse
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

confirm_orders_router = APIRouter()


@confirm_orders_router.patch("/confirm", response_model=ConfirmOrdersResponse)
@check_role(Permission.CAN_CONFIRM_ORDERS)
async def confirm_orders(
    item: ConfirmOrdersItem,
    token: TokenJwt = Depends(validate_token),
):
    if (not Session.settings.order_requires_confirmation
        or not token.permissions["can_confirm_orders"]):
        raise Unauthorized(code=ErrorCodes.NOT_ALLOWED)

    confirms_succeeded = []
    rollbacks_succeeded = []
    errors = []

    async with in_transaction() as connection:
        for order_id in item.rollbacks:
            order = await Order.get_or_none(id=order_id, using_db=connection)

            if not order:
                errors.append({"order_id": order_id, "type": "rollback",  "message": "Ordine non trovato"})
                continue
            
            try:
                await order.update_from_dict(
                    {
                        "table": None,
                        "confirmed_by_id": None,
                        "is_confirmed": False,
                        "confirmed_at": None,
                    }
                ).save(using_db=connection)

                rollbacks_succeeded.append(order_id)
            except:
                errors.append({"order_id": order_id, "type": "rollback",  "message": "Errore durante il salvataggio"})
                continue

        for confirm in item.confirms:
            order_id = confirm.order_id

            order = (
                await Order.filter(id=order_id)
                .prefetch_related("user__role")
                .using_db(connection)
                .first()
            )

            if not order:
                errors.append({"order_id": order_id, "type": "confirm", "message": "Ordine non trovato"})
                continue

            if order.user.role.order_confirmer_id != token.role_id:
                errors.append({"order_id": order_id, "type": "confirm",  "message": "Non autorizzato alla conferma di quest'ordine"})
                continue

            rome_tz = pytz.timezone("Europe/Rome")
            now_in_rome = datetime.datetime.now(rome_tz)

            try:
                update_dict = {
                    "table": confirm.table if not order.is_take_away else None,
                    "confirmed_by_id": token.user_id,
                    "is_confirmed": True,
                }
                
                if not order.is_confirmed:
                    update_dict["confirmed_at"] = now_in_rome
                
                await order.update_from_dict(update_dict).save(using_db=connection)

                confirms_succeeded.append(order_id)
            except:
                errors.append({"order_id": order_id, "type": "confirm",  "message": "Errore durante il salvataggio"})
                continue

    return ConfirmOrdersResponse(
        confirms_succeeded=confirms_succeeded,
        rollbacks_succeeded=rollbacks_succeeded,
        errors=errors
    )
