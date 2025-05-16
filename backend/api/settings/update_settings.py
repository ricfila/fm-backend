from fastapi import APIRouter, Depends
from tortoise.transactions import in_transaction

from backend.config import Session
from backend.database.models import Setting
from backend.decorators import check_role
from backend.models import BaseResponse
from backend.models.settings import UpdateSettingsItem
from backend.utils import Permission, TokenJwt, validate_token

update_settings_router = APIRouter()


@update_settings_router.put("/", response_model=BaseResponse)
@check_role(Permission.CAN_ADMINISTER)
async def update_settings(
    item: UpdateSettingsItem, token: TokenJwt = Depends(validate_token)
):
    """
    Update settings.

    **Permission**: can_administer
    """

    item_data = {k: v for k, v in item.model_dump().items() if v}

    async with in_transaction() as connection:
        setting = await Setting.first(using_db=connection)

        await setting.update_from_dict(item_data).save(using_db=connection)

        Session.settings = Session.settings.model_copy(update=item_data)

    return BaseResponse()
