from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from backend.database.models import Role
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import Conflict, NotFound, Unauthorized
from backend.models.roles import UpdateRoleOrderConfirmerItem
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

update_role_order_confirmer_router = APIRouter()


@update_role_order_confirmer_router.put(
    "/{role_id}/order_confirmer", response_model=BaseResponse
)
@check_role(Permission.CAN_ADMINISTER)
async def update_role_order_confirmer(
    role_id: int,
    item: UpdateRoleOrderConfirmerItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Update order confirmer of role.

    **Permission**: can_administer
    """

    async with in_transaction() as connection:
        role = await Role.get_or_none(id=role_id, using_db=connection)

        if not role:
            raise NotFound(code=ErrorCodes.ROLE_NOT_FOUND)

        if role.name == "admin":
            raise Unauthorized(code=ErrorCodes.NOT_ALLOWED)

        if role.name == "base":
            raise Unauthorized(code=ErrorCodes.NOT_ALLOWED)

        if not role.can_order:
            raise Unauthorized(code=ErrorCodes.NOT_ALLOWED)

        order_confirmer = await Role.get_or_none(
            id=item.order_confirmer_id, using_db=connection
        )

        if not order_confirmer:
            raise NotFound(code=ErrorCodes.ROLE_NOT_FOUND)

        if not order_confirmer.can_confirm_orders:
            raise Unauthorized(code=ErrorCodes.NOT_ALLOWED)

        role.order_confirmer = order_confirmer

        try:
            await role.save(using_db=connection)

        except IntegrityError:
            raise Conflict(code=ErrorCodes.ROLE_ALREADY_EXISTS)

    return BaseResponse()
