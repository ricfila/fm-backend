import sys

import uvicorn
from argon2 import PasswordHasher
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from backend.config import Config, Session
from backend.database import init_db
from backend.routers import load_routers

FMT = "<green>[{time}]</green> | <level>{level}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"


# Logger
logger.configure(
    handlers=[
        {"sink": sys.stdout, "format": FMT},
        {"sink": "log.log", "format": FMT},
    ]
)


# Env
load_dotenv()


# Config
conf = Session.config = Config()


# FastAPI
app = FastAPI(title="Festival Backend", docs_url="/")


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


# Database - Tortoise orm
init_db(app)


# routers
load_routers(app)


# Error
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
    uvicorn.run(app, host=conf.APP_HOST)
