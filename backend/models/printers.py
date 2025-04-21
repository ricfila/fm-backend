from pydantic import BaseModel, field_validator

from backend.models import BaseResponse
from backend.utils import validate_name_field, validate_ip_address_field


class Printer(BaseModel):
    id: int
    name: str
    ip_address: str


class PrinterName(BaseModel):
    id: int
    name: str


class CreatePrinterItem(BaseModel):
    name: str
    ip_address: str

    @field_validator("name")
    @classmethod
    def validate_name_field(cls, name: str):
        return validate_name_field(name)

    @field_validator("ip_address")
    @classmethod
    def validate_ip_address_field(cls, ip_address: str):
        return validate_ip_address_field(ip_address)


class CreatePrinterResponse(BaseResponse):
    printer: Printer


class GetPrinterResponse(BaseResponse, Printer):
    pass


class GetPrintersResponse(BaseResponse):
    total_count: int
    printers: list[Printer | PrinterName]


class UpdatePrinterNameItem(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def validate_name_field(cls, name: str):
        return validate_name_field(name)


class UpdatePrinterIpAddressItem(BaseModel):
    ip_address: str

    @field_validator("ip_address")
    @classmethod
    def validate_ip_address_field(cls, ip_address: str):
        return validate_ip_address_field(ip_address)
