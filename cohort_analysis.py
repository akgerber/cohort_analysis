from datetime import datetime, tzinfo
import dateutil
import arrow
from models import Customer, Cohort, database




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


def get_customers_for(cohort: Cohort):
    """
    Get all Customers that are members of a given cohort
    :param cohort:
    :return:
    """
    startdate = datetime(cohort.start)
    enddate = datetime(cohort.get_end())
    customers = Customer.select().where(
        Customer.created >= startdate & Customer.created <= enddate).get()
    return customers


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
        [get_customers_for(cohort) for cohort in cohorts]
