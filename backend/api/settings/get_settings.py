from fastapi import APIRouter, Depends
from tortoise.transactions import in_transaction

from backend.database.models import Setting
from backend.decorators import check_role
from backend.models.settings import GetSettingsResponse
from backend.utils import Permission, TokenJwt, validate_token

get_settings_router = APIRouter()


@get_settings_router.get("/", response_model=GetSettingsResponse)
@check_role(Permission.CAN_ADMINISTER)
async def get_settings(token: TokenJwt = Depends(validate_token)):
    """
    Get list of settings.

    **Permission**: can_administer
    """

    async with in_transaction() as connection:
        setting = await Setting.first(using_db=connection)

    return GetSettingsResponse(**await setting.to_dict())
