from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from backend.database.models import Subcategory
from backend.decorators import check_role
from backend.models.error import Conflict
from backend.models.subcategories import (
    CreateSubcategoryItem,
    CreateSubcategoryResponse,
)
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

create_subcategory_router = APIRouter()


@create_subcategory_router.post("/", response_model=CreateSubcategoryResponse)
@check_role(Permission.CAN_ADMINISTER)
async def create_subcategory(
    item: CreateSubcategoryItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Create a new subcategory.

    **Permission**: can_administer
    """

    async with in_transaction() as connection:
        new_subcategory = Subcategory(name=item.name)

        try:
            await new_subcategory.save(using_db=connection)

        except IntegrityError:
            raise Conflict(code=ErrorCodes.SUBCATEGORY_ALREADY_EXISTS)

    return CreateSubcategoryResponse(
        subcategory=await new_subcategory.to_dict()
    )
