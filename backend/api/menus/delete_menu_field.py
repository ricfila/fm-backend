from fastapi import APIRouter, Depends
from tortoise.transactions import in_transaction

from backend.database.models import Menu, MenuField
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import NotFound
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

delete_menu_field_router = APIRouter()


@delete_menu_field_router.delete(
    "/{menu_id}/field/{menu_field_id}", response_model=BaseResponse
)
@check_role(Permission.CAN_ADMINISTER)
async def delete_menu_field(
    menu_id: int,
    menu_field_id: int,
    token: TokenJwt = Depends(validate_token),
):
    """
    Delete a menu field from the id.

    **Permission**: can_administer
    """

    async with in_transaction() as connection:
        menu = await Menu.get_or_none(id=menu_id, using_db=connection)

        if not menu:
            raise NotFound(code=ErrorCodes.MENU_NOT_FOUND)

        menu_field = await MenuField.get_or_none(
            id=menu_field_id, menu=menu, using_db=connection
        )

        if not menu_field:
            raise NotFound(code=ErrorCodes.MENU_FIELD_NOT_FOUND)

        await menu_field.delete(using_db=connection)

    return BaseResponse()
