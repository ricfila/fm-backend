import asyncio

from backend.config import Config


class Session:
    config: Config = None

    @classmethod
    def set_config(cls) -> None:
        if cls.config is None:
            cls.config = Config()
