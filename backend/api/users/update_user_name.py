from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError

from backend.database.models import User
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import Conflict, NotFound, Unauthorized
from backend.models.users import UpdateUserNameItem
from backend.utils import ErrorCodes, TokenJwt, validate_token
from backend.utils.enums import Permission

update_user_name_router = APIRouter()


@update_user_name_router.put("/{user_id}/name", response_model=BaseResponse)
@check_role(Permission.CAN_ADMINISTER)
async def update_user_name(
    user_id: int,
    item: UpdateUserNameItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Update name of user.

    **Permission**: can_administer
    """

    user = await User.get_or_none(id=user_id)

    if not user:
        raise NotFound(code=ErrorCodes.USER_NOT_FOUND)

    if user.username == "admin":
        raise Unauthorized(code=ErrorCodes.NOT_ALLOWED)

    user.username = item.username

    try:
        await user.save()

    except IntegrityError:
        raise Conflict(code=ErrorCodes.USER_ALREADY_EXISTS)

    return BaseResponse()
