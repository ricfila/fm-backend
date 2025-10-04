from enum import StrEnum


class Permission(StrEnum):
    CAN_ADMINISTER = "can_administer"
    CAN_ORDER = "can_order"
    CAN_STATISTICS = "can_statistics"
    CAN_PRIORITY_STATISTICS = "can_priority_statistics"
    CAN_CONFIRM_ORDERS = "can_confirm_orders"


class PrinterType(StrEnum):
    RECEIPT = "receipt"
    TICKET = "ticket"
