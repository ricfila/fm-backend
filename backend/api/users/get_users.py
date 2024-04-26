from fastapi import APIRouter, Depends

from backend.config import Session
from backend.database.models import User
from backend.decorators import check_role
from backend.models.users import GetUsersResponse
from backend.utils import Permission, TokenJwt, validate_token

get_users_router = APIRouter()


@get_users_router.get("/", response_model=GetUsersResponse)
@check_role(Permission.CAN_ADMINISTER)
async def get_users(
    offset: int = 0,
    limit: int = Session.config.DEFAULT_LIMIT_VALUE,
    token: TokenJwt = Depends(validate_token),
):
    """
    Get list of users.

    **Permission**: can_administer
    """

    users_query = User.exclude(id=token.user_id)
    total_count = await users_query.count()
    users = await users_query.offset(offset).limit(limit)

    return GetUsersResponse(
        total_count=total_count, users=[await user.to_dict() for user in users]
    )
