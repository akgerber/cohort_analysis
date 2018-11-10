from datetime import datetime, tzinfo, timedelta
import dateutil
import arrow
from models import Customer, Order, database


class Cohort:
    """A weeklong bucket, extending from `start` to 7 days beyond
    """
    def __init__(self, start: arrow):
        self.start = start

    def get_end(self):
        return self.start.shift(weeks=+1)

    def __eq__(self, other):
        return other.start == self.start


def get_cohort_for(dt: datetime, tz: tzinfo = dateutil.tz.gettz('US/Pacific')) -> Cohort:
    """
    Place a datetime in a weeklong cohort (with weeks starting/ending in the specified timezone)
    :param dt: a datetime
    :param tz: the timezone used to determine week boundaries
    :return: a Cohort including the datetime
    """
    # use Arrow library as builtin datetime doesn't support DST changing over time
    as_tz = arrow.get(dt).to(tz)
    iso = as_tz.isocalendar()
    cohort_start = arrow.Arrow.strptime(f"{iso[0]}|{iso[1]}"+"|1", "%G|%V|%u", tz)
    return Cohort(cohort_start)


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


if __name__ == "__main__":
    with database:
        start = arrow.get(get_start_date())
        end = arrow.get(get_end_date())
        print(start)
        startcohort = get_cohort_for(start)
        print(f"{startcohort.start} {startcohort.get_end()}")
        print(end)
        endcohort = get_cohort_for(end)
        print(f"{endcohort.start} {endcohort.get_end()}")
        cohorts = [startcohort]
        while startcohort != endcohort:
            startcohort = get_cohort_for(startcohort.get_end())
            print(f"{startcohort.start} {startcohort.get_end()}")
            cohorts.append(startcohort)
        print(cohorts)
