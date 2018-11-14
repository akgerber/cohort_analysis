from datetime import datetime, tzinfo
import dateutil
import arrow
from models import WeekBucket
from service import service


def get_cohort_for(dt: datetime, tz: tzinfo = dateutil.tz.gettz('US/Pacific')) -> WeekBucket:
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
    return WeekBucket(cohort_start)


if __name__ == "__main__":
    with service.database:
        start = arrow.get(service.get_oldest_customer_date())
        end = arrow.get(service.get_newest_customer_date())
        print(start)
        startbucket = get_cohort_for(start)
        print(end)
        endbucket = get_cohort_for(end)
        buckets = [startbucket]
        while startbucket != endbucket:
            startbucket = get_cohort_for(startbucket.get_end())
            buckets.append(startbucket)
        print(buckets)
        cohorts = [service.get_new_customer_ids_for(bucket) for bucket in buckets]
        analysis = []
        for cohort in cohorts:
            order_counts = \
                [service.get_order_count_for(bucket, cohort) for bucket in buckets]
            analysis.append(order_counts)
            print(order_counts)
