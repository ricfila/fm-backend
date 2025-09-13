from pydantic import BaseModel, field_validator

from backend.models import BaseResponse
from backend.utils import validate_name_field, validate_ip_address_field


class PaymentMethod(BaseModel):
    id: int
    name: str
    order: int
    is_deleted: bool


class PaymentMethodName(BaseModel):
    id: int
    name: str
