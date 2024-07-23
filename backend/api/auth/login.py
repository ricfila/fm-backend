from argon2 import PasswordHasher
from argon2.exceptions import Argon2Error, InvalidHashError
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from tortoise.exceptions import ValidationError
from tortoise.transactions import in_transaction

from backend.database.models import User
from backend.models.auth import LoginResponse
from backend.models.error import BadRequest, Unauthorized
from backend.utils import ErrorCodes, TokenJwt, encode_jwt

login_router = APIRouter(prefix="/token")


@login_router.post("/", response_model=LoginResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Performs user authentication.
    """

    try:
        async with in_transaction():
            user = await User.get_or_none(username=form_data.username)

    except ValidationError:
        raise BadRequest(code=ErrorCodes.USERNAME_TOO_LONG)

    auth_error = Unauthorized(code=ErrorCodes.INVALID_USERNAME_OR_PASSWORD)

    if not user:
        raise auth_error

    try:
        ph = PasswordHasher()
        ph.verify(user.password, form_data.password)

    except (Argon2Error, InvalidHashError):
        raise auth_error

    payload = TokenJwt(
        user.id, user.role_id, await (await user.role).get_permissions()
    )

    return LoginResponse(access_token=encode_jwt(payload))
