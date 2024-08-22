from fastapi import APIRouter, Depends
from tortoise.transactions import in_transaction

from backend.database.models import Product, ProductIngredient
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import NotFound
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

delete_product_ingredient_router = APIRouter()


@delete_product_ingredient_router.delete(
    "/{product_id}/ingredient/{product_ingredient_id}",
    response_model=BaseResponse,
)
@check_role(Permission.CAN_ADMINISTER)
async def delete_product_ingredient(
    product_id: int,
    product_ingredient_id: int,
    token: TokenJwt = Depends(validate_token),
):
    """
    Delete a product ingredient from the id.

    **Permission**: can_administer
    """

    async with in_transaction() as connection:
        product = await Product.get_or_none(id=product_id, using_db=connection)

        if not product:
            raise NotFound(code=ErrorCodes.PRODUCT_NOT_FOUND)

        product_ingredient = await ProductIngredient.get_or_none(
            id=product_ingredient_id, product=product, using_db=connection
        )

        if not product_ingredient:
            raise NotFound(code=ErrorCodes.PRODUCT_INGREDIENT_NOT_FOUND)

        await product_ingredient.delete(using_db=connection)

    return BaseResponse()
