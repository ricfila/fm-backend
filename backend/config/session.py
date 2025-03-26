from __future__ import annotations

import typing

from backend.config import Config

if typing.TYPE_CHECKING:
    from backend.models.settings import Settings


class Session:
    config: Config = None
    settings: Settings

    @classmethod
    def set_config(cls) -> None:
        if cls.config is None:
            cls.config = Config()
