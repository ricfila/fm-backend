from fastapi import APIRouter, Depends

from backend.database.models import Ingredient
from backend.models.ingredients import GetWardsResponse
from backend.utils import TokenJwt, validate_token

get_wards_router = APIRouter()


@get_wards_router.get("/wards", response_model=GetWardsResponse)
async def get_wards(
    deleted: bool = False,
    token: TokenJwt = Depends(validate_token),
):
    """
    Get list of wards.
    """

    wards_list = await Ingredient.filter(is_deleted=deleted).distinct().values_list('ward', flat=True)

    return GetWardsResponse(
        total_count=len(wards_list),
        wards=wards_list
    )
