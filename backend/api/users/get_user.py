from fastapi import APIRouter, Depends
from tortoise.transactions import in_transaction

from backend.database.models import User
from backend.models.error import NotFound, Unauthorized
from backend.models.users import GetUserResponse
from backend.utils import ErrorCodes, TokenJwt, validate_token
from backend.utils.enums import Permission

get_user_router = APIRouter()


@get_user_router.get("/{user_id}", response_model=GetUserResponse)
async def get_user(
    user_id: int,
    token: TokenJwt = Depends(validate_token),
):
    """
    Get information about a user.
    """

    async with in_transaction() as connection:
        user = await User.get_or_none(id=user_id, using_db=connection)

        if not user:
            raise NotFound(code=ErrorCodes.USER_NOT_FOUND)

        if not (
            token.permissions.get(Permission.CAN_ADMINISTER, False)
            or token.user_id == user.id
        ):
            raise Unauthorized(code=ErrorCodes.NOT_ALLOWED)

    return GetUserResponse(
        id=user.id,
        username=user.username,
        role_id=user.role_id,
        created_at=user.created_at,
    )
