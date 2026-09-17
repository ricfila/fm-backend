from fastapi import APIRouter, Depends
from tortoise.transactions import in_transaction

from backend.config import Session
from backend.database.models import Order
from backend.database.utils import get_current_time
from backend.decorators import check_role
from backend.models.error import BadRequest
from backend.models.orders import ConfirmOrdersItem, ConfirmOrdersResponse
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token
from backend.utils.order_utils import is_table_allowed_for_role

confirm_orders_router = APIRouter()


@confirm_orders_router.patch("/confirm", response_model=ConfirmOrdersResponse)
@check_role(Permission.CAN_CONFIRM_ORDERS)
async def confirm_orders(
    item: ConfirmOrdersItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Confirm or rollback batch of orders.

     **Permission**: can_confirm_orders
    """

    if not Session.settings.order_requires_confirmation:
        raise BadRequest(code=ErrorCodes.METHOD_NOT_ALLOWED)

    confirms_succeeded = []
    rollbacks_succeeded = []
    errors = []

    async with in_transaction() as connection:
        for order_id in item.rollbacks:
            order = await Order.get_or_none(id=order_id, using_db=connection)

            if not order:
                errors.append({"order_id": order_id, "type": "rollback",  "message": "Ordine non trovato"})
                continue

            if not order.needs_confirmation:
                errors.append({"order_id": order_id, "type": "rollback",  "message": "Non è consentito dissociare il tavolo per quest'ordine"})
                continue
            
            try:
                await order.update_from_dict(
                    {
                        "table": None,
                        "confirmed_at": None,
                        "confirmed_by_id": None,
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

            if not order.needs_confirmation:
                errors.append({"order_id": order_id, "type": "confirm",  "message": "Non è consentito confermare quest'ordine"})
                continue

            if order.user.role.order_confirmer_id != token.role_id:
                errors.append({"order_id": order_id, "type": "confirm",  "message": "Utente non autorizzato alla conferma di quest'ordine"})
                continue

            if not order.is_take_away and not await is_table_allowed_for_role(
                token.role_id, confirm.table, connection
            ):
                errors.append({"order_id": order_id, "type": "confirm",  "message": "Utente non autorizzato all'associazione di questo tavolo"})
                continue

            try:
                update_dict = {
                    "table": confirm.table,
                    "confirmed_by_id": token.user_id,
                }
                
                if order.confirmed_at is None:
                    update_dict["confirmed_at"] = get_current_time()
                
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
