from fastapi import APIRouter, Depends
from tortoise.transactions import in_transaction

from backend.database.models import User
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import NotFound, Unauthorized
from backend.utils import ErrorCodes, TokenJwt, validate_token
from backend.utils.enums import Permission

delete_user_router = APIRouter()


@delete_user_router.delete("/{user_id}", response_model=BaseResponse)
@check_role(Permission.CAN_ADMINISTER)
async def delete_user(
    user_id: int,
    token: TokenJwt = Depends(validate_token),
):
    """
    Delete a user.

    **Permission**: can_administer
    """

    async with in_transaction() as connection:
        user = await User.get_or_none(id=user_id, using_db=connection)

        if not user:
            raise NotFound(code=ErrorCodes.USER_NOT_FOUND)

        if user.username == "admin":
            raise Unauthorized(code=ErrorCodes.NOT_ALLOWED)

        await user.delete(using_db=connection)

    return BaseResponse()
