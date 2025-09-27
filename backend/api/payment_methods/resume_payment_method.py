from fastapi import APIRouter, Depends
from tortoise.transactions import in_transaction

from backend.database.models import PaymentMethod
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import NotFound
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

resume_payment_method_router = APIRouter()


@resume_payment_method_router.post(
    "/{payment_method_id}", response_model=BaseResponse
)
@check_role(Permission.CAN_ADMINISTER)
async def restore_payment_method(
    payment_method_id: int, token: TokenJwt = Depends(validate_token)
):
    """
    Resume a deleted payment_method from the id.

    **Permission**: can_administer
    """

    async with in_transaction() as connection:
        payment_method = await PaymentMethod.get_or_none(
            id=payment_method_id, is_deleted=True, using_db=connection
        )

        if not payment_method:
            raise NotFound(code=ErrorCodes.PAYMENT_METHOD_NOT_FOUND)

        payment_method.is_deleted = False
        await payment_method.save(using_db=connection)

    return BaseResponse()
