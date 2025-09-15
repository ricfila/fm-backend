from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from backend.database.models import Ingredient, Product, ProductIngredient
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
        
        ingredient = await Ingredient.get_or_none(id=item.ingredient_id, using_db=connection)
        if not ingredient:
            raise NotFound(code=ErrorCodes.INGREDIENT_NOT_FOUND)
        
        product_ingredient = await ProductIngredient.get_or_none(
            product_id=product.id, ingredient_id=ingredient.id, is_deleted=True, using_db=connection
        )
        if not product_ingredient:
            product_ingredient = ProductIngredient(
                product=product,
                ingredient=ingredient,
                price=item.price,
                max_quantity=item.max_quantity,
                is_default=item.is_default
            )
        else:
            product_ingredient.price=item.price
            product_ingredient.max_quantity=item.max_quantity
            product_ingredient.is_default=item.is_default
            product_ingredient.is_deleted=False

        try:
            await product_ingredient.save(using_db=connection)

        except IntegrityError:
            raise Conflict(code=ErrorCodes.PRODUCT_INGREDIENT_ALREADY_EXISTS)

    return AddProductIngredientResponse(
        product_ingredient=await product_ingredient.to_dict_name()
    )
