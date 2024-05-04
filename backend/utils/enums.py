from enum import StrEnum


class Category(StrEnum):
    FOODS = "food"
    DRINKS = "drink"


class PaperSize(StrEnum):
    A4 = "A4"


class Permission(StrEnum):
    CAN_ADMINISTER = "can_administer"
    CAN_ORDER = "can_order"
    CAN_STATISTICS = "can_statistics"
    CAN_PRIORITY_STATISTICS = "can_priority_statistics"
