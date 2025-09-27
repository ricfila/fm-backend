from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from backend.database.models import PaymentMethod
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import NotFound
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

delete_payment_method_router = APIRouter()


@delete_payment_method_router.delete(
    "/{payment_method_id}", response_model=BaseResponse
)
@check_role(Permission.CAN_ADMINISTER)
async def delete_payment_method(
    payment_method_id: int,
    token: TokenJwt = Depends(validate_token),
):
    """
    Delete a payment method.

    **Permission**: can_administer
    """

    async with in_transaction() as connection:
        payment_method = await PaymentMethod.get_or_none(
            id=payment_method_id, using_db=connection
        )

        if not payment_method:
            raise NotFound(code=ErrorCodes.PAYMENT_METHOD_NOT_FOUND)

        payment_method.is_deleted = True
        await payment_method.save(using_db=connection)

    return BaseResponse()
