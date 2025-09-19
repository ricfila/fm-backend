from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from backend.database.models import Category, Product, Subcategory
from backend.decorators import check_role
from backend.models.error import Conflict, NotFound
from backend.models.products import CreateProductItem, CreateProductResponse
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

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

    async with in_transaction() as connection:
        category = await Category.get_or_none(
            id=item.category_id, using_db=connection
        )
        if not category:
            raise NotFound(code=ErrorCodes.CATEGORY_NOT_FOUND)
        
        subcategory = await Subcategory.get_or_none(
            id=item.subcategory_id, using_db=connection
        )
        if not subcategory:
            raise NotFound(code=ErrorCodes.SUBCATEGORY_NOT_FOUND)

        new_product = Product(
            name=item.name,
            short_name=item.short_name,
            price=item.price,
            category=category,
            subcategory=subcategory,
        )

        try:
            await new_product.save(using_db=connection)

        except IntegrityError:
            raise Conflict(code=ErrorCodes.PRODUCT_ALREADY_EXISTS)

    return CreateProductResponse(product=await new_product.to_dict())
