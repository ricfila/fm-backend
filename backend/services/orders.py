from collections import defaultdict

from tortoise import BaseDBAsyncClient

from backend.database.models import OrderMenu, OrderProduct
from backend.utils.datetime_utils import get_day_bounds


async def get_today_quantities(
    ids: set[int],
    connection: BaseDBAsyncClient,
    is_menu: bool = False,
) -> dict[int, int]:
    start_of_day, end_of_day = get_day_bounds()

    field_name = "menu_id" if is_menu else "product_id"
    model = OrderMenu if is_menu else OrderProduct

    filter_kwargs = {
        f"{field_name}__in": ids,
        "order__created_at__gte": start_of_day,
        "order__created_at__lt": end_of_day,
    }

    order_items = await model.filter(**filter_kwargs).using_db(connection)

    item_quantity_map = defaultdict(int)
    for item in order_items:
        item_id = getattr(item, field_name)
        item_quantity_map[item_id] += item.quantity

    return dict(item_quantity_map)
