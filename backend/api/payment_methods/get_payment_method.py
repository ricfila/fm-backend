from fastapi import APIRouter, Depends
from tortoise.transactions import in_transaction

from backend.database.models import PaymentMethod
from backend.decorators import check_role
from backend.models.error import NotFound
from backend.models.payment_methods import GetPaymentMethodResponse
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

get_payment_method_router = APIRouter()


@get_payment_method_router.get(
    "/{payment_method_id}", response_model=GetPaymentMethodResponse
)
@check_role(Permission.CAN_ADMINISTER, Permission.CAN_ORDER)
async def get_payment_method(
    payment_method_id: int,
    token: TokenJwt = Depends(validate_token)
):
    """
    Get information about a subcategory.

    **Permission**: can_administer, can_order
    """

    async with in_transaction() as connection:
        payment_method = await PaymentMethod.get_or_none(
            id=payment_method_id, using_db=connection
        )

        if not payment_method:
            raise NotFound(code=ErrorCodes.PAYMENT_METHOD_NOT_FOUND)

    return GetPaymentMethodResponse(
        id=payment_method_id,
        name=payment_method.name,
        order=payment_method.order,
        is_deleted=payment_method.is_deleted
    )
