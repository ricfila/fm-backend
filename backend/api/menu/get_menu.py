from fastapi import APIRouter, Depends

from backend.database.models import Menu
from backend.models.error import NotFound, Unauthorized
from backend.models.menu import GetMenuResponse
from backend.utils import TokenJwt, validate_token

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

    menu = await Menu.get_or_none(id=menu_id).prefetch_related(
        "dates", "roles"
    )

    if not menu:
        raise NotFound("Menu not found")

    if not token.permissions["can_administer"]:
        if include_dates or include_roles:
            raise Unauthorized(
                "Only an administrator can use `include_dates` or `include_roles` option"
            )

        if not any([role.role_id == token.role_id for role in menu.roles]):
            raise Unauthorized("You do not have permission to get this menu")

        if not any([await date.is_valid_menu_date() for date in menu.dates]):
            raise Unauthorized("You do not have permission to get this menu")

    return GetMenuResponse(
        **await menu.to_dict(include_dates, include_fields, include_roles)
    )
