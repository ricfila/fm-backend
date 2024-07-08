import datetime

import pytz


def is_valid_date(
    start_date: datetime.datetime, end_date: datetime.datetime
) -> bool:
    current_time = datetime.datetime.now(pytz.UTC)

    return not (current_time < start_date or current_time > end_date)
