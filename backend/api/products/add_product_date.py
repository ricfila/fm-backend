from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError

from backend.database.models import Product, ProductDate
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import Conflict, NotFound
from backend.models.products import AddProductDateItem, AddProductDateResponse
from backend.utils import Permission, TokenJwt, validate_token

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

    product = await Product.get_or_none(id=product_id)

    if not product:
        raise NotFound("Product not found")

    new_product_date = ProductDate(
        start_date=item.start_date, end_date=item.end_date, product=product
    )

    try:
        await new_product_date.save()

    except IntegrityError:
        raise Conflict("Product date already exists")

    except ValueError as e:
        raise Conflict(e.args[0])

    return AddProductDateResponse(date=await new_product_date.to_dict())
