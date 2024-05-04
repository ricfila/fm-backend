__all__ = ("products",)

from fastapi import APIRouter

products = APIRouter(prefix="/products", tags=["products"])
