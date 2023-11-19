from fastapi import APIRouter, Depends

from backend.decorators import check_role
from backend.utils import Permission, TokenJwt, validate_token

register_router = APIRouter(prefix="/register")


@register_router.post("/")
@check_role(Permission.CAN_ADMINISTER)
async def register(token: TokenJwt = Depends(validate_token)):
    return {}
