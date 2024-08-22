from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from backend.database.models import Product, ProductVariant
from backend.decorators import check_role
from backend.models.error import Conflict, NotFound
from backend.models.products import (
    AddProductVariantItem,
    AddProductVariantResponse,
)
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

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

    async with in_transaction() as connection:
        product = await Product.get_or_none(id=product_id, using_db=connection)

        if not product:
            raise NotFound(code=ErrorCodes.PRODUCT_NOT_FOUND)

        new_product_variant = ProductVariant(
            name=item.name, price=item.price, product=product
        )

        try:
            await new_product_variant.save(using_db=connection)

        except IntegrityError:
            raise Conflict(code=ErrorCodes.PRODUCT_VARIANT_ALREADY_EXISTS)

    return AddProductVariantResponse(
        variant=await new_product_variant.to_dict()
    )
