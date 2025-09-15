from fastapi import APIRouter, Depends
from tortoise.transactions import in_transaction

from backend.database.models import ProductIngredient
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import NotFound
from backend.models.products import UpdateProductIngredientItem
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

update_product_ingredient_router = APIRouter()


@update_product_ingredient_router.put(
    "/{product_id}/ingredient/{product_ingredient_id}", response_model=BaseResponse
)
@check_role(Permission.CAN_ADMINISTER)
async def update_product_ingredient(
    product_ingredient_id: int,
    item: UpdateProductIngredientItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Update ingredient of product.

     **Permission**: can_administer
    """

    async with in_transaction() as connection:
        product_ingredient = await ProductIngredient.get_or_none(id=product_ingredient_id, using_db=connection)

        if not product_ingredient:
            raise NotFound(code=ErrorCodes.PRODUCT_INGREDIENT_NOT_FOUND)

        product_ingredient.price = item.price
        product_ingredient.max_quantity = item.max_quantity
        product_ingredient.is_default = item.is_default

        await product_ingredient.save(using_db=connection)

    return BaseResponse()
