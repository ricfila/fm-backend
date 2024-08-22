from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from backend.database.models import Product, ProductDate
from backend.decorators import check_role
from backend.models.error import Conflict, NotFound
from backend.models.products import AddProductDateItem, AddProductDateResponse
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

add_product_date_router = APIRouter()


@add_product_date_router.post(
    "/{product_id}/date", response_model=AddProductDateResponse
)
@check_role(Permission.CAN_ADMINISTER)
async def add_product_date(
    product_id: int,
    item: AddProductDateItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Add product date.

    **Permission**: can_administer
    """

    async with in_transaction() as connection:
        product = await Product.get_or_none(id=product_id, using_db=connection)

        if not product:
            raise NotFound(code=ErrorCodes.PRODUCT_NOT_FOUND)

        new_product_date = ProductDate(
            start_date=item.start_date, end_date=item.end_date, product=product
        )

        try:
            await new_product_date.save(using_db=connection)

        except IntegrityError:
            raise Conflict(code=ErrorCodes.PRODUCT_DATE_ALREADY_EXISTS)

        except ValueError as e:
            raise Conflict(code=e.args[0])

    return AddProductDateResponse(date=await new_product_date.to_dict())
