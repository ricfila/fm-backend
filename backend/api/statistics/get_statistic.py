import datetime
from collections import defaultdict
from decimal import Decimal
import re

from fastapi import APIRouter, Depends
from tortoise.expressions import Q
from tortoise.transactions import in_transaction

from backend.database.models import Order
from backend.decorators import check_role
from backend.models.error import UnprocessableEntity
from backend.models.statistics import GetStatisticResponse, StatisticProduct
from backend.utils import Permission, TokenJwt, validate_token, ErrorCodes

ROLE_ID_REGEX = re.compile(r"^\d+(,\d+)*$")

get_statistic_router = APIRouter()


@get_statistic_router.get("/", response_model=GetStatisticResponse)
@check_role(Permission.CAN_STATISTICS, Permission.CAN_PRIORITY_STATISTICS)
async def get_statistic(
    start_date: datetime.date | None = None,
    end_date: datetime.date | None = None,
    role_ids: str | None = None,
    token: TokenJwt = Depends(validate_token),
):
    """
    Get statistic.

    **Permission**: can_statistics || can_priority_statistics
    """

    query_filters = Q()
    can_priority_statistics = token.permissions["can_priority_statistics"]

    if start_date:
        query_filters &= Q(created_at__gt=start_date)
    if end_date:
        query_filters &= Q(created_at__lt=end_date)
    if role_ids:
        if not ROLE_ID_REGEX.fullmatch(role_ids):
            raise UnprocessableEntity(code=ErrorCodes.REQUEST_VALIDATION_ERROR)

        role_ids = list(map(int, role_ids.split(",")))
        query_filters &= Q(user__role_id__in=role_ids)

    async with in_transaction() as connection:
        orders = (
            await Order.filter(query_filters, is_deleted=False)
            .prefetch_related("order_products__product", "order_menus__menu")
            .using_db(connection)
        )

        total_take_away = sum(1 for order in orders if order.is_take_away)
        total_seated = sum(
            order.guests or 0 for order in orders if not order.is_take_away
        )
        total_price_with_cover = Decimal(
            sum(
                Decimal(order.price)
                for order in orders
                if not order.is_voucher
            )
        )

        total_price_without_cover = Decimal("0.00")
        result_map: dict[str, dict[str, Decimal | int]] = defaultdict(
            lambda: {"quantity": 0, "total_price": Decimal("0.00")}
        )

        for order in orders:
            is_voucher = order.is_voucher

            order_products = [
                (op, op.product.name)
                for op in order.order_products
                if op.order_menu_field_id is None
                and (not can_priority_statistics or op.product.is_priority)
            ]
            order_menus = [
                (om, om.menu.name)
                for om in order.order_menus
                if not can_priority_statistics
            ]

            for x, name in order_products + order_menus:
                result_map[name]["quantity"] += x.quantity
                price_to_add = (
                    Decimal("0.00") if is_voucher else Decimal(x.price)
                )
                result_map[name]["total_price"] += price_to_add

                if not is_voucher:
                    total_price_without_cover += Decimal(x.price)

        result = [
            StatisticProduct(
                name=name,
                quantity=values["quantity"],
                price=(values["total_price"] / values["quantity"])
                if values["quantity"]
                else Decimal("0.00"),
                total_price=values["total_price"],
            )
            for name, values in result_map.items()
        ]

    return GetStatisticResponse(
        total_orders=len(orders),
        total_seated=total_seated,
        total_take_away=total_take_away,
        total_price_with_cover=total_price_with_cover,
        total_price_without_cover=total_price_without_cover,
        products=result,
    )
