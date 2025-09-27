from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from backend.database.models import PaymentMethod
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import Conflict, NotFound
from backend.models.payment_methods import UpdatePaymentMethodItem
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

update_payment_method_router = APIRouter()


@update_payment_method_router.put(
    "/{payment_method_id}", response_model=BaseResponse
)
@check_role(Permission.CAN_ADMINISTER)
async def update_payment_method(
    payment_method_id: int,
    item: UpdatePaymentMethodItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Update a payment method.

    **Permission**: can_administer
    """

    async with in_transaction() as connection:
        payment_method = await PaymentMethod.get_or_none(
            id=payment_method_id, using_db=connection
        )

        if not payment_method:
            raise NotFound(code=ErrorCodes.PAYMENT_METHOD_NOT_FOUND)

        payment_method.name = item.name
        payment_method.order = item.order

        try:
            await payment_method.save(using_db=connection)

        except IntegrityError:
            raise Conflict(code=ErrorCodes.PAYMENT_METHOD_ALREADY_EXISTS)

    return BaseResponse()
