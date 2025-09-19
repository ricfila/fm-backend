from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from backend.database.models import Category
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import Conflict, NotFound
from backend.models.categories import UpdateParentCategoryItem
from backend.utils.categories import check_cyclic_links
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

update_category_parent_main_products_router = APIRouter()


@update_category_parent_main_products_router.put("/{category_id}/parent_main_products", response_model=BaseResponse)
@check_role(Permission.CAN_ADMINISTER)
async def update_category_parent_main_products(
    category_id: int,
    item: UpdateParentCategoryItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Update a parent category for main products.

     **Permission**: can_administer
    """

    async with in_transaction() as connection:
        category = await Category.get_or_none(id=category_id, using_db=connection)
        if not category:
            raise NotFound(code=ErrorCodes.CATEGORY_NOT_FOUND)

        if item.parent_category_id is None:
            category.parent_for_main_products = None
        else:
            parent = await Category.get_or_none(id=item.parent_category_id, using_db=connection)
            if not parent:
                raise NotFound(code=ErrorCodes.PARENT_CATEGORY_NOT_FOUND)
            
            await check_cyclic_links(category_id, parent, 'parent_for_main_products')
            
            category.parent_for_main_products = parent

        try:
            await category.save(using_db=connection)

        except IntegrityError:
            raise Conflict(code=ErrorCodes.CATEGORY_ALREADY_EXISTS)

    return BaseResponse()
