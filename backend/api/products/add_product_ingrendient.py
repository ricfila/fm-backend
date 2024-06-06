from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError

from backend.database.models import Product, ProductIngredient
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import Conflict, NotFound
from backend.models.products import AddProductIngredientItem, AddProductIngredientResponse
from backend.utils import Permission, TokenJwt, validate_token

add_product_ingredient_router = APIRouter()


@add_product_ingredient_router.post(
    "/{product_id}/ingredient", response_model=AddProductIngredientResponse
)
@check_role(Permission.CAN_ADMINISTER)
async def add_product_ingredient(
    product_id: int,
    item: AddProductIngredientItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Add product ingredient.

    **Permission**: can_administer
    """

    product = await Product.get_or_none(id=product_id)

    if not product:
        raise NotFound("Product not found")

    new_product_ingredient = ProductIngredient(
        name=item.name, price=item.price, product=product
    )

    try:
        await new_product_ingredient.save()

    except IntegrityError:
        raise Conflict("Product ingredient already exists")

    return AddProductIngredientResponse(ingredient=await new_product_ingredient.to_dict())
