from enum import Enum, auto


class ErrorCodes(Enum):
    SUCCESS = 0

    # Auth
    # Login
    INVALID_USERNAME_OR_PASSWORD = auto()
    USERNAME_TOO_LONG = auto()

    # Register
    CANNOT_CREATE_ADMIN_USER = auto()
    USER_ALREADY_EXISTS = auto()

    # Orders
    # Create
    INPUT_MENU_FIELD_PRODUCT_VARIANT = auto()
    INPUT_PRODUCT_VARIANT = auto()
    MENU_DATE_NOT_VALID = auto()
    MENU_FIELD_NOT_EXIST = auto()
    MENU_FIELD_PRODUCT_INGREDIENT_NOT_EXIST = auto()
    MENU_FIELD_PRODUCT_VARIANT_NOT_EXIST = auto()
    MENU_FIELD_PRODUCT_NOT_EXIST = auto()
    MENU_FIELD_TOO_MANY_PRODUCTS = auto()
    MENU_NOT_EXIST = auto()
    MENU_ROLE_NOT_EXIST = auto()
    MISSING_MENU_FIELD_PRODUCTS = auto()
    MISSING_OBLIGATORY_MENU_FIELDS = auto()
    MISSING_PRODUCT_QUANTITY = auto()
    NO_PRODUCTS_AND_MENUS = auto()
    PRODUCT_DATE_NOT_VALID = auto()
    PRODUCT_INGREDIENT_NOT_EXIST = auto()
    PRODUCT_NOT_EXIST = auto()
    PRODUCT_ROLE_NOT_EXIST = auto()
    PRODUCT_VARIANT_NOT_EXIST = auto()
    SET_GUESTS_NUMBER = auto()

    # Roles
    ROLE_NOT_FOUND = auto()
    # Create
    ROLE_ALREADY_EXISTS = auto()

    # Subcategories
    SUBCATEGORY_NOT_FOUND = auto()
    # Create
    SUBCATEGORY_ALREADY_EXISTS = auto()

    # Users
    USER_NOT_FOUND = auto()

    # Token
    INVALID_JWT_TOKEN = auto()

    # Permission
    NOT_ALLOWED = auto()
    NOT_AUTHENTICATED = auto()

    # Validation
    ONLY_ONE_STATISTICS_CAN_BE_TRUE = auto()
    PAPER_SIZE_REQUIRED_IF_CAN_ORDER = auto()
    UNKNOWN_ORDER_BY_PARAMETER = auto()

    # Default
    GENERIC_HTTP_EXCEPTION = auto()
    INTERNAL_ERROR_SERVER = auto()
    REQUEST_VALIDATION_ERROR = auto()
