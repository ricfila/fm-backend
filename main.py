import sys

import uvicorn
from fastapi import FastAPI
from loguru import logger

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

if __name__ == "__main__":
    uvicorn.run(app)
