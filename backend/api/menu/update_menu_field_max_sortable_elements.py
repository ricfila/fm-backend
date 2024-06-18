from fastapi import APIRouter, Depends

from backend.database.models import Menu, MenuField
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import NotFound
from backend.models.menu import UpdateMenuFieldMaxSortableElementsItem
from backend.utils import Permission, TokenJwt, validate_token

update_menu_field_max_sortable_elements_router = APIRouter()


@update_menu_field_max_sortable_elements_router.put(
    "/{menu_id}/field/{menu_field_id}/max_sortable_elements",
    response_model=BaseResponse,
)
@check_role(Permission.CAN_ADMINISTER)
async def update_menu_field_max_sortable_elements(
    menu_id: int,
    menu_field_id: int,
    item: UpdateMenuFieldMaxSortableElementsItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Update max sortable elements of menu field.

    **Permission**: can_administer
    """

    menu = await Menu.get_or_none(id=menu_id)

    if not menu:
        raise NotFound("Menu not found")

    menu_field = await MenuField.get_or_none(id=menu_field_id, menu=menu)

    if not menu_field:
        raise NotFound("Menu field not found")

    menu_field.max_sortable_elements = item.max_sortable_elements

    await menu_field.save()

    return BaseResponse()
