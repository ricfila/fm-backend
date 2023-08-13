import importlib
import pathlib

from fastapi import APIRouter, FastAPI


def load_routers(app: FastAPI):
    path = pathlib.Path(__file__).parent
    package = ".".join(path.relative_to(pathlib.Path(".").absolute()).parts)
    files = list(
        filter(lambda x: not x.name.startswith("_"), path.glob("*.py"))
    )

    for x in files:
        module = importlib.import_module(f"{package}.{x.stem}")

        for v in module.__dict__.values():
            if isinstance(v, APIRouter):
                app.include_router(v)
