from fastapi import APIRouter, Depends
from tortoise.exceptions import FieldError

from backend.database.models import Menu
from backend.models.error import NotFound, Unauthorized
from backend.models.menu import GetMenusResponse
from backend.utils import TokenJwt, validate_token

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

    menus_query = Menu.all().prefetch_related("dates", "roles")

    if order_by:
        try:
            menus_query = menus_query.order_by(order_by)
        except FieldError:
            raise NotFound("Unknown order_by parameter")

    if not token.permissions["can_administer"]:
        if include_dates or include_roles:
            raise Unauthorized(
                "Only an administrator can use `include_dates` or `include_roles` option"
            )

        invalid_menu_ids = set()

        async for menu in menus_query:
            if not any(
                [await date.is_valid_menu_date() for date in menu.dates]
            ):
                invalid_menu_ids.add(menu.id)

            if not any([role.role_id == token.role_id for role in menu.roles]):
                invalid_menu_ids.add(menu.id)

        menus_query = menus_query.exclude(id__in=invalid_menu_ids)

    total_count = await menus_query.count()

    if not limit:
        limit = total_count - offset

    menus = await menus_query.offset(offset).limit(limit)

    return GetMenusResponse(
        total_count=total_count,
        menus=[
            await menu.to_dict(
                include_dates,
                include_fields,
                include_roles,
            )
            for menu in menus
        ],
    )
