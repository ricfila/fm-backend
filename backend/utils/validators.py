from backend.utils.enums import Permission


def validate_username_field(username: str):
    if not username:
        raise ValueError("The `username` field can not be empty")

    if len(username) > 32:
        raise ValueError(
            "The `username` field must have a maximum length of 32 characters"
        )

    if not username.isalpha():
        raise ValueError("The `username` field has illegal characters")

    return username


def validate_password_field(password: str):
    if not password:
        raise ValueError("The `password` field can not be empty")

    if len(password) > 32:
        raise ValueError(
            "The `password` field must have a maximum length of 32 characters"
        )

    return password


def validate_name_field(name: str):
    if not name:
        raise ValueError("The `name` field can not be empty")

    if len(name) > 32:
        raise ValueError(
            "The `name` field must have a maximum length of 32 characters"
        )

    return name


def validate_permissions_field(permissions: dict[Permission, bool]):
    if (
        Permission.CAN_ADMINISTER in permissions
        and permissions[Permission.CAN_ADMINISTER]
    ):
        raise ValueError("The `permissions` field can't be administrators")

    return permissions


def validate_order_field(order: int):
    if order < 0:
        raise ValueError(
            "The `order` field must be greater than or equal to 0"
        )

    return order
