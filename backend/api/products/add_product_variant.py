from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError

from backend.database.models import Product, ProductVariant
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import Conflict, NotFound
from backend.models.products import AddProductVariantItem, AddProductVariantResponse
from backend.utils import Permission, TokenJwt, validate_token

add_product_variant_router = APIRouter()


@add_product_variant_router.post(
    "/{product_id}/variant", response_model=AddProductVariantResponse
)
@check_role(Permission.CAN_ADMINISTER)
async def add_product_variant(
    product_id: int,
    item: AddProductVariantItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Add product variant.

    **Permission**: can_administer
    """

    product = await Product.get_or_none(id=product_id)

    if not product:
        raise NotFound("Product not found")

    new_product_variant = ProductVariant(
        name=item.name, price=item.price, product=product
    )

    try:
        await new_product_variant.save()

    except IntegrityError:
        raise Conflict("Product variant already exists")

    return AddProductVariantResponse(variant=await new_product_variant.to_dict())
