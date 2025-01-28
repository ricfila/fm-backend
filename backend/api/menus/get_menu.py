from fastapi import APIRouter, Depends
from tortoise.transactions import in_transaction

from backend.database.models import Menu
from backend.models.error import NotFound
from backend.models.menu import GetMenuResponse
from backend.utils import ErrorCodes, TokenJwt, validate_token
from backend.utils.query_filters import build_single_query_filter

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
        query_filter = build_single_query_filter(
            menu_id, token, include_dates, include_roles
        )

        menu = (
            await Menu.filter(query_filter)
            .prefetch_related("dates", "menu_fields__field_products", "roles")
            .using_db(connection)
            .first()
        )

        if not menu:
            raise NotFound(code=ErrorCodes.MENU_NOT_FOUND)

    return GetMenuResponse(
        **await menu.to_dict(include_dates, include_fields, include_roles)
    )
