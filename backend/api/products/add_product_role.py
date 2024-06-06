from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError

from backend.database.models import Product, ProductRole, Role
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import Conflict, NotFound, Unauthorized
from backend.models.products import AddProductRoleItem, AddProductRoleResponse
from backend.utils import Permission, TokenJwt, validate_token

add_product_role_router = APIRouter()


@add_product_role_router.post(
    "/{product_id}/role", response_model=AddProductRoleResponse
)
@check_role(Permission.CAN_ADMINISTER)
async def add_product_role(
    product_id: int,
    item: AddProductRoleItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Add product role.

    **Permission**: can_administer
    """

    product = await Product.get_or_none(id=product_id)

    if not product:
        raise NotFound("Product not found")

    role = await Role.get_or_none(id=item.role_id)

    if not role:
        raise NotFound("Role not found")

    if not role.can_order:
        raise Unauthorized("The role can not order")

    new_product_role = ProductRole(role=role, product=product)

    try:
        await new_product_role.save()

    except IntegrityError:
        raise Conflict("Product role already exists")

    return AddProductRoleResponse(role=await new_product_role.to_dict())
