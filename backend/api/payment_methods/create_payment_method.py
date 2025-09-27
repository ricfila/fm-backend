from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from backend.database.models import PaymentMethod
from backend.decorators import check_role
from backend.models.error import Conflict
from backend.models.payment_methods import (
    CreatePaymentMethodItem,
    CreatePaymentMethodResponse,
)
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

create_payment_method_router = APIRouter()


@create_payment_method_router.post("/", response_model=CreatePaymentMethodResponse)
@check_role(Permission.CAN_ADMINISTER)
async def create_payment_method(
    item: CreatePaymentMethodItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Create a new payment_method.

    **Permission**: can_administer
    """

    async with in_transaction() as connection:
        new_payment_method = PaymentMethod(name=item.name)
        print(new_payment_method.to_dict())

        try:
            await new_payment_method.save(using_db=connection)

        except IntegrityError:
            raise Conflict(code=ErrorCodes.PAYMENT_METHOD_ALREADY_EXISTS)

    return CreatePaymentMethodResponse(
        payment_method=await new_payment_method.to_dict()
    )
