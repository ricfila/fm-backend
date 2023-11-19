import functools

from backend.database.models import Role
from backend.models.error import Forbidden
from backend.utils import Permission, TokenJwt


def check_role(*permission: Permission):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(token: TokenJwt, *args, **kwargs):
            role = await Role.get_or_none(id=token.role_id)
            error = Forbidden("Not allowed")

            if not role:
                raise error

            if not all(map(lambda x: getattr(role, x, False), permission)):
                raise error

            return await func(token=token, *args, **kwargs)

        return wrapper

    return decorator
