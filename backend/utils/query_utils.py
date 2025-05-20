from datetime import date, timedelta
from typing import Type, TypeVar

from tortoise import Model, BaseDBAsyncClient
from tortoise.exceptions import FieldError
from tortoise.expressions import Q, F, Expression
from tortoise.functions import Sum
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


async def get_orderable_entities(
    relation_name: str,
    quantity_field: str,
    order_date_field: str = "created_at",
    max_daily_field: str = "daily_max_sales",
    for_date: date = None,
):
    today = for_date or date.today()
    tomorrow = today + timedelta(days=1)

    quantity_path = f"{relation_name}__{quantity_field}"
    date_path = f"{relation_name}__order__{order_date_field}"

    date_filter = Q(**{f"{date_path}__gte": today}) & Q(
        **{f"{date_path}__lt": tomorrow}
    )

    annotate_expression = {
        "total_quantity": Sum(F(quantity_path), _filter=date_filter)
    }

    availability_filter = (
        Q(**{f"{max_daily_field}__isnull": True})
        | Q(total_quantity__lt=F(max_daily_field))
        | Q(total_quantity__isnull=True)
    )

    return annotate_expression, availability_filter
