from fastapi import APIRouter, Depends
from tortoise.exceptions import ParamsError
from tortoise.expressions import Q
from tortoise.query_utils import Prefetch
from tortoise.transactions import in_transaction

from backend.database.models import Product, ProductIngredient, ProductVariant
from backend.models.error import BadRequest
from backend.models.products import (
    GetProductsResponse,
    Product as ProductModel,
    ProductName,
)
from backend.services.orders import get_today_quantities
from backend.utils import ErrorCodes, TokenJwt, validate_token
from backend.utils.query_filters import build_multiple_query_filter
from backend.utils.query_utils import process_query_with_pagination
from backend.services.ingredients import get_ingredient_stock

get_products_router = APIRouter()


@get_products_router.get("/", response_model=GetProductsResponse)
async def get_products(
    offset: int = 0,
    limit: int | None = None,
    only_name: bool = False,
    order_by: str = None,
    category_id: int = None,
    subcategory_id: int = None,
    include_dates: bool = False,
    include_ingredients: bool = False,
    include_roles: bool = False,
    include_subcategory: bool = False,
    include_variants: bool = False,
    include_locks: bool = False,
    token: TokenJwt = Depends(validate_token),
):
    """
    Get list of products.
    """

    async with in_transaction() as connection:
        products_query_filter = build_multiple_query_filter(
            token, include_dates, include_roles
        )

        if category_id:
            products_query_filter &= Q(category_id=category_id)

        if subcategory_id:
            products_query_filter &= Q(subcategory_id=subcategory_id)

        (products_query, _, limit,) = await process_query_with_pagination(
            Product,
            products_query_filter,
            connection,
            offset,
            limit,
            order_by,
        )

        try:
            products = (
                await products_query.prefetch_related(
                    "dates",
                    "roles",
                    Prefetch(
                        "ingredients",
                        queryset=ProductIngredient.filter(is_deleted=False),
                    ),
                    Prefetch(
                        "variants",
                        queryset=ProductVariant.filter(is_deleted=False),
                    ),
                )
                .offset(offset)
                .limit(limit)
            )
        except ParamsError:
            raise BadRequest(code=ErrorCodes.INVALID_OFFSET_OR_LIMIT_NEGATIVE)

        if not token.permissions["can_administer"]:
            product_ids = {p.id for p in products if p.daily_max_sales}
            today_quantities = await get_today_quantities(
                product_ids, connection
            )

            products = [
                p
                for p in products
                if not p.daily_max_sales
                or today_quantities.get(p.id, 0) < p.daily_max_sales
            ]
        
        ingredient_stock_levels = {}
        if include_locks:
            ingredients = await get_ingredient_stock(connection, only_locked=True)
            for ing in ingredients:
                added = ing["added_stock"] if ing["added_stock"] is not None else 0
                ingredient_stock_levels[ing["id"]] = added - ing["consumed_stock"]

    return GetProductsResponse(
        total_count=len(products),
        products=[
            ProductName(**await product.to_dict_name())
            if only_name
            else ProductModel(
                **await product.to_dict(
                    include_dates,
                    include_ingredients,
                    include_roles,
                    include_subcategory,
                    include_variants,
                ),
                locked=(
                    len([
                        ing
                        for ing in product.ingredients
                        if ing.is_default and ing.max_quantity > ingredient_stock_levels.get(ing.ingredient_id, ing.max_quantity)]
                    ) > 0
                ) if include_locks else None
            )
            for product in products
        ],
    )
