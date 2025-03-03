from fastapi import APIRouter, Depends
from tortoise.exceptions import ParamsError
from tortoise.expressions import Q
from tortoise.transactions import in_transaction

from backend.database.models import Subcategory
from backend.models.error import BadRequest
from backend.models.subcategories import (
    GetSubcategoriesResponse,
    Subcategory as SubcategoryModel,
    SubcategoryName,
)
from backend.utils import ErrorCodes, TokenJwt, validate_token
from backend.utils.query_utils import process_query_with_pagination

get_subcategories_router = APIRouter()


@get_subcategories_router.get("/", response_model=GetSubcategoriesResponse)
async def get_subcategories(
    offset: int = 0,
    limit: int | None = None,
    only_name: bool = False,
    order_by: str = None,
    token: TokenJwt = Depends(validate_token),
):
    """
    Get list of subcategories.

    **Permission**: can_administer
    """

    async with in_transaction() as connection:
        (
            subcategories_query,
            total_count,
            limit,
        ) = process_query_with_pagination(
            Subcategory, Q(), connection, offset, limit, order_by
        )

        try:
            subcategories = await subcategories_query.offset(offset).limit(
                limit
            )
        except ParamsError:
            raise BadRequest(code=ErrorCodes.INVALID_OFFSET_OR_LIMIT_NEGATIVE)

    return GetSubcategoriesResponse(
        total_count=total_count,
        subcategories=[
            SubcategoryName(**await subcategory.to_dict_name())
            if only_name
            else SubcategoryModel(**await subcategory.to_dict())
            for subcategory in subcategories
        ],
    )
