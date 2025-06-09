from typing import Type, TypeVar

from tortoise import Model, BaseDBAsyncClient
from tortoise.exceptions import FieldError
from tortoise.expressions import Q, Expression
from tortoise.queryset import QuerySet

from backend.models.error import NotFound
from backend.utils import ErrorCodes

T = TypeVar("T", bound=Model)


async def process_query_with_pagination(
    model: Type[T],
    query_filter: Q,
    connection: BaseDBAsyncClient,
    offset: int,
    limit: int,
    order_by: str,
    annotate_expression: dict[str, Expression] = None,
) -> tuple[QuerySet[T], int, int]:
    query = model

    if annotate_expression:
        query = query.annotate(**annotate_expression)

    query = query.filter(query_filter).using_db(connection)
    total_count = await query.count()

    if not limit:
        limit = total_count - offset

    if order_by:
        try:
            query = query.order_by(order_by)
        except FieldError:
            raise NotFound(code=ErrorCodes.UNKNOWN_ORDER_BY_PARAMETER)

    return query, total_count, limit
