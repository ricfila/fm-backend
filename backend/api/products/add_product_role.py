from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from backend.database.models import Product, ProductRole, Role
from backend.decorators import check_role
from backend.models.error import Conflict, NotFound, Unauthorized
from backend.models.products import AddProductRoleItem, AddProductRoleResponse
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

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

    async with in_transaction() as connection:
        product = await Product.get_or_none(id=product_id, using_db=connection)

        if not product:
            raise NotFound(code=ErrorCodes.PRODUCT_NOT_FOUND)

        role = await Role.get_or_none(id=item.role_id, using_db=connection)

        if not role:
            raise NotFound(code=ErrorCodes.ROLE_NOT_FOUND)

        if not role.can_order:
            raise Unauthorized(code=ErrorCodes.ROLE_CANNOT_ORDER)

        new_product_role = ProductRole(role=role, product=product)

        try:
            await new_product_role.save(using_db=connection)

        except IntegrityError:
            raise Conflict(code=ErrorCodes.PRODUCT_ROLE_ALREADY_EXISTS)

    return AddProductRoleResponse(role=await new_product_role.to_dict())
