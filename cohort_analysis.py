from datetime import datetime, tzinfo, timedelta
import dateutil
import arrow
from models import Customer, Order, database


class Cohort:
    def __init__(self, start: datetime, length: timedelta):
        self.start = start
        self.length = length


def get_start_date() -> datetime:
    """
    Get the oldest customer's creation date
    """
    oldest = Customer.select().order_by(Customer.created).get()
    return oldest.created


def get_end_date() -> datetime:
    """
    Get the newest customer's creation date
    """
    newest = Customer.select().order_by(Customer.created.desc()).get()
    return newest.created


def get_week_bucket(dt: datetime, tz: tzinfo = dateutil.tz.gettz('US/Pacific')) -> str:
    """
    Get a unique bucket name for all datetimes in a week (in the optionally-specific timezone)
    :param dt: a datetime
    :param tz: the used to determine week boundaries
    :return: the bucket name
    """
    astz = arrow.get(dt).to(tz)
    return astz.strftime("%Y%W")


if __name__ == "__main__":
    with database:
        start = get_start_date()
        print(start)
        end = get_end_date()
        print(end)
