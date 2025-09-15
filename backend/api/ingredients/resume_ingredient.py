from fastapi import APIRouter, Depends
from tortoise.transactions import in_transaction

from backend.database.models import Ingredient
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import NotFound
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

resume_ingredient_router = APIRouter()


@resume_ingredient_router.post("/{ingredient_id}", response_model=BaseResponse)
@check_role(Permission.CAN_ADMINISTER)
async def restore_ingredient(
    ingredient_id: int, token: TokenJwt = Depends(validate_token)
):
    """
    Resume a deleted ingredient from the id.

    **Permission**: can_administer
    """

    async with in_transaction() as connection:
        ingredient = await Ingredient.get_or_none(id=ingredient_id, is_deleted=True, using_db=connection)

        if not ingredient:
            raise NotFound(code=ErrorCodes.INGREDIENT_NOT_FOUND)

        ingredient.is_deleted = False
        await ingredient.save(using_db=connection)

    return BaseResponse()
