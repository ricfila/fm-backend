import datetime

from tortoise import timezone


def get_current_time() -> datetime.datetime:
    return timezone.now()


def is_valid_date(
    start_date: datetime.datetime, end_date: datetime.datetime
) -> bool:
    current_time = get_current_time()

    return start_date < current_time < end_date
