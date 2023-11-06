import contextlib
import secrets
import string
import sys

import uvicorn
from argon2 import PasswordHasher
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from backend.api import api
from backend.config import Session
from backend.database import init_db, stop_db
from backend.database.models import Role, User
from backend.models import UnicornException

ALPHABET = string.ascii_letters + string.digits
FMT = (
    "<green>[{time}]</green> | <level>{level}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:"
    "<cyan>{line}</cyan> - <level>{message}</level>"
)

# Logger
logger.configure(
    handlers=[
        {"sink": sys.stdout, "format": FMT},
        {
            "sink": "log.log",
            "format": FMT,
            "rotation": "1 day",
            "retention": "7 days",
        },
    ]
)


# Create admin user and role - if not exist
@contextlib.asynccontextmanager
async def lifespan(_: FastAPI):
    # Database - TortoiseORM
    await init_db()
    logger.info(f"Tortoise-ORM started")

    password = "".join(secrets.choice(ALPHABET) for _ in range(8))
    role, _ = await Role.get_or_create(
        name="admin", defaults={"can_administer": True}
    )
    _, created = await User.get_or_create(
        username="admin",
        defaults={"password": PasswordHasher().hash(password), "role": role},
    )

    if created:
        logger.info(f"Created the admin user with password {password}")

    yield

    await stop_db()
    logger.info("Tortoise-ORM shutdown")


# Config - Pydantic
Session.set_config()
logger.info("Initializing Config")

# FastAPI - instance
app = FastAPI(title="FestivalBackend", docs_url="/", lifespan=lifespan)
logger.info("Starting FastAPI application")

# CORS
origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info("Setting CORS")

# FastAPI - APIRouter
app.include_router(api)
logger.info("Initializing API routers")


# Handling Errors
@app.exception_handler(UnicornException)
async def unicorn_exception_handler(_: Request, exc: UnicornException):
    return JSONResponse(
        status_code=exc.status, content={"error": True, "message": exc.message}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    _: Request, exc: RequestValidationError
):
    detail = exc.errors()

    return JSONResponse(
        status_code=422,
        content={
            "error": True,
            "message": "Request Validation Error",
            "detail": detail,
        },
    )


if __name__ == "__main__":
    uvicorn.run(app, host=Session.config.APP_HOST)
