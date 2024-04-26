from fastapi import APIRouter, Depends

from backend.database.models import User
from backend.utils.enums import Permission
from backend.models.users import GetUserResponse
from backend.models.error import Unauthorized, NotFound
from backend.utils import TokenJwt, validate_token

get_user_router = APIRouter()


@get_user_router.get("/{user_id}", response_model=GetUserResponse)
async def get_user(
    user_id: int,
    token: TokenJwt = Depends(validate_token),
):
    """
    Get information about a user.

    **Permission**: can_administer
    """

    user = await User.get_or_none(id=user_id)

    if not user:
        raise NotFound("User not found")

    if not (
        token.permissions.get(Permission.CAN_ADMINISTER, False)
        or token.user_id == user.id
    ):
        raise Unauthorized("You do not have permission to perform this")

    return GetUserResponse(
        id=user.id,
        username=user.username,
        role_id=user.role_id,
        created_at=user.created_at,
    )
