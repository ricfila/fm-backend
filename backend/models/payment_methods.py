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


class CreatePaymentMethodItem(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def validate_name_field(cls, name: str):
        return validate_name_field(name)


class CreatePaymentMethodResponse(BaseResponse):
    payment_method: PaymentMethod


class GetPaymentMethodsResponse(BaseResponse):
    total_count: int
    payment_methods: list[PaymentMethod | PaymentMethodName]


class GetPaymentMethodResponse(BaseResponse, PaymentMethod):
    pass


class UpdatePaymentMethodItem(BaseModel):
    name: str
    order: int

    @field_validator("name")
    @classmethod
    def validate_name_field(cls, name: str):
        return validate_name_field(name)
