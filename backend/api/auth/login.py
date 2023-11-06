from argon2 import PasswordHasher
from argon2.exceptions import Argon2Error, InvalidHashError
from fastapi import APIRouter
from tortoise.exceptions import ValidationError

from backend.database.models import User
from backend.models.auth import LoginResponse
from backend.models.error import Unauthorized, BadRequest
from backend.utils import TokenJwt, encode_jwt

login_router = APIRouter()


@login_router.get("/", response_model=LoginResponse)
async def login(username: str, password: str):
    """
    Performs user authentication.
    """

    try:
        user = await User.get_or_none(username=username)
    except ValidationError:
        raise BadRequest("Username too long.")

    if not user:
        raise Unauthorized("Invalid username or password.")

    try:
        ph = PasswordHasher()
        ph.verify(user.password, password)

    except (Argon2Error, InvalidHashError):
        raise Unauthorized("Invalid username or password.")

    payload = TokenJwt(username, user.role_id)

    return LoginResponse(token=encode_jwt(payload))
