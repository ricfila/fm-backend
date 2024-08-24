from fastapi import APIRouter, Depends
from tortoise.transactions import in_transaction

from backend.database.models import Menu, MenuField
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import NotFound
from backend.models.menu import UpdateMenuFieldIsOptionalItem
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

update_menu_field_is_optional_router = APIRouter()


@update_menu_field_is_optional_router.put(
    "/{menu_id}/field/{menu_field_id}/is_optional", response_model=BaseResponse
)
@check_role(Permission.CAN_ADMINISTER)
async def update_menu_field_is_optional(
    menu_id: int,
    menu_field_id: int,
    item: UpdateMenuFieldIsOptionalItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Update is_optional of menu field.

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

        menu_field.is_optional = item.is_optional

        await menu_field.save(using_db=connection)

    return BaseResponse()
