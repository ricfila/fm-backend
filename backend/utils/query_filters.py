from tortoise.expressions import Q

from backend.database.utils import get_current_time
from backend.models.error import Unauthorized
from backend.utils import ErrorCodes, TokenJwt


def build_common_filters(
    token: TokenJwt,
    include_dates: bool,
    include_roles: bool,
    include_fields_products_dates: bool,
    include_fields_products_roles: bool,
):
    query_filter = Q()
    current_time = get_current_time()

    if not token.permissions["can_administer"]:
        if (
            include_dates
            or include_roles
            or include_fields_products_dates
            or include_fields_products_roles
        ):
            raise Unauthorized(code=ErrorCodes.ADMIN_OPTION_REQUIRED)

        # Add a filter for the role
        query_filter &= Q(roles__role_id=token.role_id)

        # Add a filter for valid dates
        query_filter &= Q(
            dates__start_date__lte=current_time,
            dates__end_date__gte=current_time,
        )

    return query_filter


def build_single_query_filter(
    item_id: int,
    token: TokenJwt,
    include_dates: bool,
    include_roles: bool,
    include_fields_products_dates: bool = False,
    include_fields_products_roles: bool = False,
) -> Q:
    query_filter = Q(id=item_id)

    query_filter &= build_common_filters(
        token,
        include_dates,
        include_roles,
        include_fields_products_dates,
        include_fields_products_roles,
    )

    return query_filter


def build_multiple_query_filter(
    token: TokenJwt,
    include_dates: bool,
    include_roles: bool,
    include_fields_products_dates: bool = False,
    include_fields_products_roles: bool = False,
) -> Q:
    return build_common_filters(
        token,
        include_dates,
        include_roles,
        include_fields_products_dates,
        include_fields_products_roles,
    )
