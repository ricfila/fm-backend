from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from backend.database.models import Menu, MenuField
from backend.decorators import check_role
from backend.models.error import Conflict, NotFound
from backend.models.menu import AddMenuFieldItem, AddMenuFieldResponse
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

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

    async with in_transaction() as connection:
        menu = await Menu.get_or_none(id=menu_id, using_db=connection)

        if not menu:
            raise NotFound(code=ErrorCodes.MENU_NOT_FOUND)

        new_menu_field = MenuField(
            name=item.name,
            max_sortable_elements=item.max_sortable_elements,
            additional_cost=item.additional_cost,
            menu=menu,
        )

        try:
            await new_menu_field.save(using_db=connection)

        except IntegrityError:
            raise Conflict(code=ErrorCodes.MENU_FIELD_ALREADY_EXISTS)

    return AddMenuFieldResponse(field=await new_menu_field.to_dict())
