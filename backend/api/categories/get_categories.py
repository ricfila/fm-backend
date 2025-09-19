from fastapi import APIRouter, Depends
from tortoise.exceptions import ParamsError
from tortoise.expressions import Q
from tortoise.transactions import in_transaction

from backend.database.models import Category
from backend.models.error import BadRequest
from backend.models.categories import (
    GetCategoriesResponse,
    Category as CategoryModel,
    CategoryName,
)
from backend.utils import ErrorCodes, TokenJwt, validate_token
from backend.utils.query_utils import process_query_with_pagination

get_categories_router = APIRouter()


@get_categories_router.get("/", response_model=GetCategoriesResponse)
async def get_categories(
    offset: int = 0,
    limit: int | None = None,
    only_name: bool = False,
    order_by: str = None,
    token: TokenJwt = Depends(validate_token),
):
    """
    Get list of categories.

    **Permission**: can_administer
    """

    async with in_transaction() as connection:
        (
            categories_query,
            total_count,
            limit,
        ) = await process_query_with_pagination(
            Category, Q(), connection, offset, limit, order_by
        )

        try:
            categories = await categories_query.offset(offset).limit(
                limit
            )
        except ParamsError:
            raise BadRequest(code=ErrorCodes.INVALID_OFFSET_OR_LIMIT_NEGATIVE)

    return GetCategoriesResponse(
        total_count=total_count,
        categories=[
            CategoryName(**await category.to_dict_name())
            if only_name
            else CategoryModel(**await category.to_dict())
            for category in categories
        ],
    )
