from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from backend.database.models import Menu, MenuField, MenuFieldProduct, Product
from backend.decorators import check_role
from backend.models.error import Conflict, NotFound
from backend.models.menu import (
    AddMenuFieldProductItem,
    AddMenuFieldProductResponse,
)
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

add_menu_field_product_router = APIRouter()


@add_menu_field_product_router.post(
    "/{menu_id}/field/{menu_field_id}/product",
    response_model=AddMenuFieldProductResponse,
)
@check_role(Permission.CAN_ADMINISTER)
async def add_menu_field_product(
    menu_id: int,
    menu_field_id: int,
    item: AddMenuFieldProductItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Add menu field product.

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

        product = await Product.get_or_none(
            id=item.product_id, using_db=connection
        )

        if not product:
            raise NotFound(code=ErrorCodes.PRODUCT_NOT_FOUND)

        new_menu_field_product = MenuFieldProduct(
            price=item.price, product=product, menu_field=menu_field
        )

        try:
            await new_menu_field_product.save(using_db=connection)

        except IntegrityError:
            raise Conflict(code=ErrorCodes.MENU_FIELD_PRODUCT_ALREADY_EXISTS)

    return AddMenuFieldProductResponse(
        field_product=await new_menu_field_product.to_dict()
    )
