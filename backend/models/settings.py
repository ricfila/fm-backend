from pydantic import BaseModel, Field, field_validator

from backend.models import BaseResponse
from backend.utils.validators import validate_receipt_header_field


class Settings(BaseModel):
    order_requires_confirmation: bool | None = None
    receipt_header: str | None = None
    cover_charge: float | None = Field(ge=0, default=None)


class GetSettingsResponse(BaseResponse, Settings):
    pass


class UpdateSettingsItem(Settings):
    @field_validator("receipt_header")
    @classmethod
    def validate_receipt_header_field(cls, receipt_header: str):
        return validate_receipt_header_field(receipt_header)
