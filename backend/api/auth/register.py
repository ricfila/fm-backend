from argon2 import PasswordHasher
from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from backend.database.models import Role, User
from backend.decorators import check_role
from backend.models.auth import RegisterItem, RegisterUserResponse
from backend.models.error import BadRequest, Conflict, NotFound
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

register_router = APIRouter(prefix="/register")


@register_router.post("/", response_model=RegisterUserResponse)
@check_role(Permission.CAN_ADMINISTER)
async def register(
    item: RegisterItem, token: TokenJwt = Depends(validate_token)
):
    role = await Role.get_or_none(id=item.role_id)

    if not role:
        raise NotFound(code=ErrorCodes.ROLE_NOT_FOUND)

    if role.can_administer:
        raise BadRequest(code=ErrorCodes.CANNOT_CREATE_ADMIN_USER)

    try:
        ph = PasswordHasher()

        async with in_transaction():
            user = User(
                username=item.username,
                password=ph.hash(item.password),
                role=role,
            )

            await user.save()
    except IntegrityError:
        raise Conflict(code=ErrorCodes.USER_ALREADY_EXISTS)

    return RegisterUserResponse(user=await user.to_dict())
