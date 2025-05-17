from fastapi import APIRouter, Depends
from tortoise.transactions import in_transaction

from backend.database.models import Setting
from backend.models.settings import GetSettingsResponse, Settings, SettingsUser
from backend.utils import TokenJwt, validate_token

get_settings_router = APIRouter()


@get_settings_router.get("/", response_model=GetSettingsResponse)
async def get_settings(token: TokenJwt = Depends(validate_token)):
    """
    Get list of settings.

    **Permission**: can_administer
    """

    async with in_transaction() as connection:
        setting = await Setting.first(using_db=connection)

    return GetSettingsResponse(
        settings=Settings(**await setting.to_dict())
        if token.permissions["can_administer"]
        else SettingsUser(**await setting.to_dict())
    )
