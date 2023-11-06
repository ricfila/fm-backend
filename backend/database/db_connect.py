import re

from tortoise import Tortoise, connections

from backend.config import Session
from backend.database import models


def is_snake_case(string):
    pattern = r"^[a-z]+(_[a-z]+)*$"
    return bool(re.match(pattern, string))


async def init_db():
    conf = Session.config

    await Tortoise.init(
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
        }
    )


async def stop_db():
    await connections.close_all()
