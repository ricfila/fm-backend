from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from backend.database.models import Category, Printer
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import Conflict, NotFound
from backend.models.categories import UpdateCategoryPrinterItem
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

update_category_printer_router = APIRouter()


@update_category_printer_router.put("/{category_id}/printer", response_model=BaseResponse)
@check_role(Permission.CAN_ADMINISTER)
async def update_category_printer(
    category_id: int,
    item: UpdateCategoryPrinterItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Update the printer of a category.

     **Permission**: can_administer
    """

    async with in_transaction() as connection:
        category = await Category.get_or_none(id=category_id, using_db=connection)
        if not category:
            raise NotFound(code=ErrorCodes.CATEGORY_NOT_FOUND)

        if item.printer_id is None:
            category.printer = None
        else:
            printer = await Printer.get_or_none(id=item.printer_id, using_db=connection)
            if not printer:
                raise NotFound(code=ErrorCodes.PRINTER_NOT_FOUND)
            
            category.printer = printer

        try:
            await category.save(using_db=connection)

        except IntegrityError:
            raise Conflict(code=ErrorCodes.CATEGORY_ALREADY_EXISTS)

    return BaseResponse()
