from datetime import date, datetime, timedelta, timezone


def get_day_bounds(for_date: date = None):
    target_date = for_date or date.today()
    start_of_day = datetime.combine(target_date, datetime.min.time()).replace(
        tzinfo=timezone.utc
    )
    end_of_day = start_of_day + timedelta(days=1)
    return start_of_day, end_of_day
