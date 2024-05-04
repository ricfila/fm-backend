from fastapi import APIRouter, Depends
from tortoise.exceptions import FieldError

from backend.config import Session
from backend.database.models import Product
from backend.decorators import check_role
from backend.models.error import NotFound
from backend.models.products import (
    GetProductsResponse,
    Product as ProductModel,
    ProductName,
)
from backend.utils import Permission, TokenJwt, validate_token

get_products_router = APIRouter()


@get_products_router.get("/", response_model=GetProductsResponse)
@check_role(Permission.CAN_ADMINISTER)
async def get_products(
    offset: int = 0,
    limit: int | None = None,
    only_name: bool = False,
    order_by: str = None,
    subcategory_id: int = None,
    token: TokenJwt = Depends(validate_token),
):
    """
    Get list of products.

    **Permission**: can_administer
    """

    products_query = Product.all()

    if order_by:
        try:
            products_query = products_query.order_by(order_by)
        except FieldError:
            raise NotFound("Unknown order_by parameter")

    if subcategory_id:
        products_query = products_query.filter(subcategory_id=subcategory_id)

    total_count = await products_query.count()

    if not limit:
        limit = (
            total_count - offset
            if only_name
            else Session.config.DEFAULT_LIMIT_VALUE
        )

    products = await products_query.offset(offset).limit(limit)

    return GetProductsResponse(
        total_count=total_count,
        products=[
            ProductName(**await product.to_dict_name())
            if only_name
            else ProductModel(**await product.to_dict())
            for product in products
        ],
    )
