from fastapi import APIRouter, Depends
from tortoise.exceptions import ParamsError
from tortoise.expressions import Q
from tortoise.transactions import in_transaction

from backend.config import Session
from backend.database.models import User
from backend.decorators import check_role
from backend.models.error import BadRequest
from backend.models.users import GetUsersResponse
from backend.utils import Permission, TokenJwt, validate_token, ErrorCodes
from backend.utils.query_utils import process_query_with_pagination

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

    async with in_transaction() as connection:
        query = ~Q(id=token.user_id)

        users_query, total_count, limit = await process_query_with_pagination(
            User, query, connection, offset, limit, ""
        )

        try:
            users = await users_query.offset(offset).limit(limit)
        except ParamsError:
            raise BadRequest(code=ErrorCodes.INVALID_OFFSET_OR_LIMIT_NEGATIVE)

    return GetUsersResponse(
        total_count=total_count, users=[await user.to_dict() for user in users]
    )
