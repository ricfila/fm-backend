from fastapi import APIRouter, Depends
from tortoise.exceptions import FieldError

from backend.database.models import Product
from backend.models.error import NotFound, Unauthorized
from backend.models.products import (
    GetProductsResponse,
    Product as ProductModel,
    ProductAdministrator,
    ProductName,
)
from backend.utils import TokenJwt, validate_token

get_products_router = APIRouter()


@get_products_router.get("/", response_model=GetProductsResponse)
async def get_products(
    offset: int = 0,
    limit: int | None = None,
    only_name: bool = False,
    order_by: str = None,
    subcategory_id: int = None,
    include_dates: bool = False,
    include_ingredients: bool = False,
    include_roles: bool = False,
    include_variants: bool = False,
    token: TokenJwt = Depends(validate_token),
):
    """
    Get list of products.
    """

    products_query = Product.all().prefetch_related("dates", "roles")

    if order_by:
        try:
            products_query = products_query.order_by(order_by)
        except FieldError:
            raise NotFound("Unknown order_by parameter")

    if subcategory_id:
        products_query = products_query.filter(subcategory_id=subcategory_id)

    if not token.permissions["can_administer"]:
        if include_dates or include_roles:
            raise Unauthorized(
                "Only an administrator can use `include_dates` or `include_roles` option"
            )

        invalid_product_ids = set()

        async for product in products_query:
            if not any(
                [await date.is_valid_product_date() for date in product.dates]
            ):
                invalid_product_ids.add(product.id)

            if not any(
                [role.role_id == token.role_id for role in product.roles]
            ):
                invalid_product_ids.add(product.id)

        products_query = products_query.exclude(id__in=invalid_product_ids)

    total_count = await products_query.count()

    if not limit:
        limit = total_count - offset

    products_response = []
    products = await products_query.offset(offset).limit(limit)

    for product in products:
        if only_name:
            products_response.append(
                ProductName(**await product.to_dict_name())
            )
        elif token.permissions["can_administer"]:
            products_response.append(
                ProductAdministrator(
                    **await product.to_dict(
                        include_dates,
                        include_ingredients,
                        include_roles,
                        include_variants,
                    )
                )
            )
        else:
            products_response.append(
                ProductModel(
                    **await product.to_dict(
                        False, include_ingredients, False, include_variants
                    )
                )
            )

    return GetProductsResponse(
        total_count=total_count,
        products=products_response,
    )
