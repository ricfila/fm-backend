from asyncio import Lock

from pydantic import Field
from pydantic_settings import BaseSettings


class Config(BaseSettings, case_sensitive=True):
    # db
    DB_USERNAME: str = Field(alias="DB_USERNAME")
    PASSWORD: str = Field(alias="DB_PASSWORD")
    HOST: str = Field(alias="DB_HOST")
    PORT: str = Field("5432", alias="DB_PORT")
    DB_NAME: str = Field(alias="DB_NAME")

    # token jwt
    JWT_SECRET: str = Field(alias="JWT_SECRET")
    JWT_TOKEN_EXPIRES: int = Field(alias="JWT_TOKEN_EXPIRES")

    # Project
    APP_HOST: str = Field(alias="APP_HOST")

    # look
    LOCK: Lock = Lock()
