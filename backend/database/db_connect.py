import re

from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

from backend.config import Session
from backend.database import models


def is_snake_case(string):
    pattern = r"^[a-z]+(_[a-z]+)*$"
    return bool(re.match(pattern, string))


def init_db(app: FastAPI):
    conf = Session.config

    register_tortoise(
        app,
        config={
            "connections": {
                "default": {
                    "engine": "tortoise.backends.asyncpg",
                    "credentials": {
                        "host": conf.DB_HOST,
                        "port": conf.DB_PORT,
                        "user": conf.DB_USERNAME,
                        "password": conf.DB_PASSWORD,
                        "database": conf.DB_NAME,
                    },
                }
            },
            "apps": {
                "models": {
                    "models": list(
                        map(
                            lambda x: f"backend.database.models.{x}",
                            filter(lambda x: is_snake_case(x), dir(models)),
                        )
                    ),
                    "default_connection": "default",
                }
            },
            "timezone": "Europe/Rome",
        },
        generate_schemas=True,
    )
