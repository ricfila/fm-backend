import sys

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from backend.config import Session
from backend.api import api

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

# FastAPI - instance
logger.info("Start FastAPI application")
app = FastAPI(title="FestivalBackend", docs_url="/")

# Config
Session.set_config()

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

# FastAPI - APIRouter
app.include_router(api)

if __name__ == "__main__":
    uvicorn.run(app)
