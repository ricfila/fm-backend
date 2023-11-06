import dataclasses
import datetime

import jwt
from fastapi import Header
from jwt.exceptions import PyJWTError

from backend.config import Session
from backend.models.error import Unauthorized


@dataclasses.dataclass
class TokenJwt:
    username: str
    role_id: int
    exp: int = None

    def to_dict(self):
        return dict(
            username=self.username,
            role_id=self.role_id,
            exp=self.exp,
        )


def encode_jwt(payload: TokenJwt) -> str:
    payload.exp = datetime.datetime.now(
        tz=datetime.timezone.utc
    ) + datetime.timedelta(seconds=Session.config.JWT_TOKEN_EXPIRES)

    return jwt.encode(
        payload.to_dict(), Session.config.JWT_SECRET, algorithm="HS256"
    )


def decode_jwt(token: str) -> TokenJwt | None:
    try:
        result = jwt.decode(
            token, Session.config.JWT_SECRET, algorithms=["HS256"]
        )

        return TokenJwt(**result)
    except PyJWTError:
        return None


async def validate_token(
    access_token: str = Header(alias="Authorization"),
) -> TokenJwt:
    try:
        token = decode_jwt(access_token.split("Bearer ")[1])

        if not token:
            raise Unauthorized("Invalid JWT token")

        return token
    except IndexError:
        raise Unauthorized("Invalid JWT token")
