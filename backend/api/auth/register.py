from fastapi import APIRouter, Depends

from backend.utils import TokenJwt, validate_token

register_router = APIRouter(prefix="/register")


@register_router.post("/")
async def register(token: TokenJwt = Depends(validate_token)):
    return {}
