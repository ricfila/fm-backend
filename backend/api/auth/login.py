from fastapi import APIRouter

login_router = APIRouter()


@login_router.get("/")
async def login():
    return {}
