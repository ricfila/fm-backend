from fastapi import APIRouter, Depends
from tortoise.expressions import Q
from tortoise.transactions import in_transaction

from backend.database.models import Menu
from backend.database.utils import get_current_time
from backend.models.error import NotFound, Unauthorized
from backend.models.menu import GetMenuResponse
from backend.utils import ErrorCodes, TokenJwt, validate_token

get_menu_router = APIRouter()


@get_menu_router.get("/{menu_id}", response_model=GetMenuResponse)
async def get_menu(
    menu_id: int,
    include_dates: bool = False,
    include_fields: bool = False,
    include_roles: bool = False,
    token: TokenJwt = Depends(validate_token),
):
    """
    Get information about a menu.
    """

    async with in_transaction() as connection:
        query_filter = Q(id=menu_id)
        current_time = get_current_time()

        if not token.permissions["can_administer"]:
            if include_dates or include_roles:
                raise Unauthorized(code=ErrorCodes.ADMIN_OPTION_REQUIRED)

            # Add a filter for the role
            query_filter &= Q(roles__role_id=token.role_id)

            # Add a filter for valid dates
            query_filter &= Q(
                dates__start_date__lt=current_time,
                dates__end_date__gt=current_time,
            )

        menu = (
            await Menu.filter(query_filter)
            .prefetch_related("dates", "menu_fields", "roles")
            .using_db(connection)
            .first()
        )

        if not menu:
            raise NotFound(code=ErrorCodes.MENU_NOT_FOUND)

    return GetMenuResponse(
        **await menu.to_dict(include_dates, include_fields, include_roles)
    )
