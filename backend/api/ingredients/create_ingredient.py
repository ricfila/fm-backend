from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from backend.database.models import Ingredient
from backend.decorators import check_role
from backend.models.error import Conflict
from backend.models.ingredients import CreateIngredientItem, CreateIngredientResponse
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

create_ingredient_router = APIRouter()


@create_ingredient_router.post("/", response_model=CreateIngredientResponse)
@check_role(Permission.CAN_ADMINISTER)
async def create_ingredient(
    item: CreateIngredientItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Create a new ingredient.

    **Permission**: can_administer
    """

    async with in_transaction() as connection:

        new_ingredient = Ingredient(
            name=item.name,
            ward=item.ward,
            is_monitored=item.is_monitored,
            cooking_time=item.cooking_time
        )

        try:
            await new_ingredient.save(using_db=connection)

        except IntegrityError:
            raise Conflict(code=ErrorCodes.INGREDIENT_ALREADY_EXISTS)

    return CreateIngredientResponse(ingredient=await new_ingredient.to_dict())
