from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError

from backend.database.models import Menu, MenuField
from backend.decorators import check_role
from backend.models.error import Conflict, NotFound
from backend.models.menu import AddMenuFieldItem, AddMenuFieldResponse
from backend.utils import Permission, TokenJwt, validate_token

add_menu_field_router = APIRouter()


@add_menu_field_router.post(
    "/{menu_id}/field", response_model=AddMenuFieldResponse
)
@check_role(Permission.CAN_ADMINISTER)
async def add_menu_field(
    menu_id: int,
    item: AddMenuFieldItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Add menu field.

    **Permission**: can_administer
    """

    menu = await Menu.get_or_none(id=menu_id)

    if not menu:
        raise NotFound("Menu not found")

    new_menu_field = MenuField(
        name=item.name,
        max_sortable_elements=item.max_sortable_elements,
        menu=menu,
    )

    try:
        await new_menu_field.save()

    except IntegrityError:
        raise Conflict("Menu field already exists")

    return AddMenuFieldResponse(field=await new_menu_field.to_dict())
