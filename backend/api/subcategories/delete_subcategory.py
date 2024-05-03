from fastapi import APIRouter, Depends

from backend.database.models import Subcategory
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.error import NotFound
from backend.utils import Permission, TokenJwt, validate_token

delete_subcategories_router = APIRouter()


@delete_subcategories_router.delete(
    "/{subcategory_id}", response_model=BaseResponse
)
@check_role(Permission.CAN_ADMINISTER)
async def delete_subcategory(
    subcategory_id: int, token: TokenJwt = Depends(validate_token)
):
    """
    Delete a subcategory from the id.

     **Permission**: can_administer
    """

    subcategory = await Subcategory.get_or_none(id=subcategory_id)

    if not subcategory:
        raise NotFound("Subcategory not found")

    await subcategory.delete()

    return BaseResponse()
