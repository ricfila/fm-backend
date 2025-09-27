from fastapi import APIRouter, Depends
from tortoise.exceptions import ParamsError
from tortoise.expressions import Q
from tortoise.transactions import in_transaction

from backend.database.models import PaymentMethod
from backend.decorators import check_role
from backend.models.error import BadRequest
from backend.models.payment_methods import (
    GetPaymentMethodsResponse,
    PaymentMethod as PaymentMethodModel,
    PaymentMethodName,
)
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token
from backend.utils.query_utils import process_query_with_pagination

get_payment_methods_router = APIRouter()

@get_payment_methods_router.get("/", response_model=GetPaymentMethodsResponse)
@check_role(Permission.CAN_ADMINISTER, Permission.CAN_ORDER)
async def get_payment_methods(
    offset: int = 0,
    limit: int | None = None,
    only_name: bool = False,
    order_by: str = None,
    token: TokenJwt = Depends(validate_token),
):
    """
    Get list of payment_methods.

    **Permission**: can_administer, can_order
    """

    async with in_transaction() as connection:
        (
            payment_methods_query,
            total_count,
            limit,
        ) = await process_query_with_pagination(
            PaymentMethod, Q(is_deleted=False), connection, offset, limit, order_by
        )

        try:
            payment_methods = await payment_methods_query.offset(offset).limit(limit)
        except ParamsError:
            raise BadRequest(code=ErrorCodes.INVALID_OFFSET_OR_LIMIT_NEGATIVE)

    return GetPaymentMethodsResponse(
        total_count=total_count,
        payment_methods=[
            PaymentMethodName(**await payment_method.to_dict_name())
            if only_name
            else PaymentMethodModel(**await payment_method.to_dict())
            for payment_method in payment_methods
        ],
    )
