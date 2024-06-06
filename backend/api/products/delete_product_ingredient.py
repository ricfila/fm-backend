from fastapi import APIRouter, Depends

from backend.database.models import Product, ProductIngredient
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import NotFound
from backend.utils import Permission, TokenJwt, validate_token

delete_product_ingredient_router = APIRouter()


@delete_product_ingredient_router.delete(
    "/{product_id}/ingredient/{product_ingredient_id}", response_model=BaseResponse
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

    product = await Product.get_or_none(id=product_id)

    if not product:
        raise NotFound("Product not found")

    product_ingredient = await ProductIngredient.get_or_none(
        id=product_ingredient_id, product=product
    )

    if not product_ingredient:
        raise NotFound("Product ingredient not found")

    await product_ingredient.delete()

    return BaseResponse()
