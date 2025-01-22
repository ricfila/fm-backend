from fastapi import APIRouter, Depends
from tortoise.exceptions import FieldError, ParamsError
from tortoise.expressions import Q
from tortoise.transactions import in_transaction

from backend.database.models import Menu
from backend.database.utils import get_current_time
from backend.models.error import NotFound, Unauthorized, BadRequest
from backend.models.menu import GetMenusResponse, Menu as MenuModel
from backend.utils import ErrorCodes, TokenJwt, validate_token

get_menus_router = APIRouter()


@get_menus_router.get("/", response_model=GetMenusResponse)
async def get_menus(
    offset: int = 0,
    limit: int | None = None,
    order_by: str = None,
    include_dates: bool = False,
    include_fields: bool = False,
    include_roles: bool = False,
    token: TokenJwt = Depends(validate_token),
):
    """
    Get list of menu.
    """

    async with in_transaction() as connection:
        menus_query_filter = Q()
        current_time = get_current_time()

        if not token.permissions["can_administer"]:
            if include_dates or include_roles:
                raise Unauthorized(code=ErrorCodes.ADMIN_OPTION_REQUIRED)

            # Add a filter for the role
            menus_query_filter &= Q(roles__role_id=token.role_id)

            # Add a filter for valid dates
            menus_query_filter &= Q(
                dates__start_date__lt=current_time,
                dates__end_date__gt=current_time,
            )

        menus_query = Menu.filter(menus_query_filter).using_db(connection)

        total_count = await menus_query.count()

        if not limit:
            limit = total_count - offset

        if order_by:
            try:
                menus_query = menus_query.order_by(order_by)
            except FieldError:
                raise NotFound(code=ErrorCodes.UNKNOWN_ORDER_BY_PARAMETER)

        try:
            menus = (
                await menus_query.prefetch_related(
                    "dates", "menu_fields__field_products", "roles"
                )
                .offset(offset)
                .limit(limit)
            )
        except ParamsError:
            raise BadRequest(code=ErrorCodes.INVALID_OFFSET_OR_LIMIT_NEGATIVE)

    return GetMenusResponse(
        total_count=total_count,
        menus=[
            MenuModel(
                **await menu.to_dict(
                    include_dates,
                    include_fields,
                    include_roles,
                )
            )
            for menu in menus
        ],
    )
