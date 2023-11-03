from pydantic import Field
from pydantic_settings import BaseSettings


class Config(BaseSettings, case_sensitive=True):
    # Db
    DB_USERNAME: str = Field(alias="DB_USERNAME")
    DB_PASSWORD: str = Field(alias="DB_PASSWORD")
    DB_HOST: str = Field(alias="DB_HOST")
    DB_PORT: str = Field("5432", alias="DB_PORT")
    DB_NAME: str = Field(alias="DB_NAME")

    # Token jwt
    JWT_SECRET: str = Field(alias="JWT_SECRET")
    JWT_TOKEN_EXPIRES: int = Field(alias="JWT_TOKEN_EXPIRES")

    # Project
    APP_HOST: str = Field(alias="APP_HOST")
