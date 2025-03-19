from pydantic import BaseModel

from backend.models import BaseResponse


class Settings(BaseModel):
    order_requires_confirmation: bool


class GetSettingsResponse(BaseResponse, Settings):
    pass


class UpdateSettingsItem(Settings):
    pass
