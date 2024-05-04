from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError

from backend.database.models import Product, Subcategory
from backend.decorators import check_role
from backend.models.error import Conflict, NotFound
from backend.models.products import CreateProductItem, CreateProductResponse
from backend.utils import Permission, TokenJwt, validate_token

create_product_router = APIRouter()


@create_product_router.post("/", response_model=CreateProductResponse)
@check_role(Permission.CAN_ADMINISTER)
async def create_product(
    item: CreateProductItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Create a new product.

    **Permission**: can_administer
    """

    subcategory = await Subcategory.get_or_none(id=item.subcategory_id)

    if not subcategory:
        raise NotFound("Subcategory not found")

    new_product = Product(
        name=item.name,
        short_name=item.short_name,
        price=item.price,
        category=item.category,
        subcategory=subcategory,
    )

    try:
        await new_product.save()

    except IntegrityError:
        raise Conflict("Product already exists")

    return CreateProductResponse(product=await new_product.to_dict())
