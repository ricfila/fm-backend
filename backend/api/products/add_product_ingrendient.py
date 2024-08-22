from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from backend.database.models import Product, ProductIngredient
from backend.decorators import check_role
from backend.models.error import Conflict, NotFound
from backend.models.products import (
    AddProductIngredientItem,
    AddProductIngredientResponse,
)
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

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

    async with in_transaction() as connection:
        product = await Product.get_or_none(id=product_id, using_db=connection)

        if not product:
            raise NotFound(code=ErrorCodes.PRODUCT_NOT_FOUND)

        new_product_ingredient = ProductIngredient(
            name=item.name, price=item.price, product=product
        )

        try:
            await new_product_ingredient.save(using_db=connection)

        except IntegrityError:
            raise Conflict(code=ErrorCodes.PRODUCT_INGREDIENT_ALREADY_EXISTS)

    return AddProductIngredientResponse(
        ingredient=await new_product_ingredient.to_dict()
    )
