import datetime
from zoneinfo import ZoneInfo


def get_current_time() -> datetime.datetime:
    tz = ZoneInfo("Europe/Rome")

    return datetime.datetime.now(tz)


def is_valid_date(
    start_date: datetime.datetime, end_date: datetime.datetime
) -> bool:
    current_time = get_current_time()

    return start_date < current_time < end_date
