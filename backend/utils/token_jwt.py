import dataclasses
import datetime

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import PyJWTError

from backend.config import Session
from backend.models.error import Unauthorized

OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl="auth/token")


@dataclasses.dataclass
class TokenJwt:
    user_id: int
    role_id: int
    permissions: dict[str, bool]
    exp: int = None

    def to_dict(self):
        return dict(
            user_id=self.user_id,
            role_id=self.role_id,
            permissions=self.permissions,
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
    access_token: str = Depends(OAUTH2_SCHEME),
) -> TokenJwt:
    token = decode_jwt(access_token)

    if not token:
        raise Unauthorized("Invalid JWT token")

    return token
