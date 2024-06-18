from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError

from backend.database.models import Menu, MenuField, MenuFieldProduct, Product
from backend.decorators import check_role
from backend.models.error import Conflict, NotFound
from backend.models.menu import (
    AddMenuFieldProductItem,
    AddMenuFieldProductResponse,
)
from backend.utils import Permission, TokenJwt, validate_token

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

    menu = await Menu.get_or_none(id=menu_id)

    if not menu:
        raise NotFound("Menu not found")

    menu_field = await MenuField.get_or_none(id=menu_field_id, menu=menu)

    if not menu_field:
        raise NotFound("Menu field not found")

    product = await Product.get_or_none(id=item.product_id)

    if not product:
        raise NotFound("Product not found")

    new_menu_field_product = MenuFieldProduct(
        price=item.price, product=product, menu_field=menu_field
    )

    try:
        await new_menu_field_product.save()

    except IntegrityError:
        raise Conflict("Menu field product already exists")

    return AddMenuFieldProductResponse(
        field_product=await new_menu_field_product.to_dict()
    )
