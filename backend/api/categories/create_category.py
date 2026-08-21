from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from backend.database.models import Category, Printer
from backend.decorators import check_role
from backend.models.error import Conflict
from backend.models.categories import (
    CreateCategoryItem,
    CreateCategoryResponse,
)
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

create_category_router = APIRouter()


@create_category_router.post("/", response_model=CreateCategoryResponse)
@check_role(Permission.CAN_ADMINISTER)
async def create_category(
    item: CreateCategoryItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Create a new category.

    **Permission**: can_administer
    """

    async with in_transaction() as connection:
        printer = await Printer.get_or_none(id=item.printer_id, using_db=connection)
        if not printer:
            raise Conflict(code=ErrorCodes.PRINTER_NOT_FOUND)

        new_category = Category(
            name=item.name,
            printer=printer,
            print_delay=item.print_delay
        )

        try:
            await new_category.save(using_db=connection)

        except IntegrityError:
            raise Conflict(code=ErrorCodes.CATEGORY_ALREADY_EXISTS)

    return CreateCategoryResponse(
        category=await new_category.to_dict()
    )
