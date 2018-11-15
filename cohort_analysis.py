from datetime import datetime, tzinfo
import dateutil
import arrow
from models import WeekBucket
from service import service


def get_bucket_for(dt: datetime, tz: tzinfo = dateutil.tz.gettz('US/Pacific'))\
        -> WeekBucket:
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


def get_buckets_for_range(first: WeekBucket, last: WeekBucket) -> [WeekBucket]:
    bucket_range = [first]
    while first != last:
        first = get_bucket_for(first.get_end())
        bucket_range.append(first)
    return bucket_range


if __name__ == "__main__":
    utc = dateutil.tz.gettz('UTC')
    start = service.get_oldest_customer_date()
    end = service.get_newest_customer_date()
    order_end = service.get_newest_order_date()
    first_cohort = get_bucket_for(start)
    last_cohort = get_bucket_for(end)
    last_order_bucket = get_bucket_for(order_end)
    cohorts = get_buckets_for_range(first_cohort, last_cohort)
    order_analyses = []
    first_order_analyses = []
    for cohort in cohorts:
        cohort_ids = service.get_new_customer_ids_for(cohort)
        buckets = get_buckets_for_range(cohort, last_order_bucket)
        order_analysis = []
        first_order_analysis = []
        orders = service.get_orders_for(cohort_ids)
        seen = set()
        pos = 0
        print(len(cohort_ids))
        for bucket in buckets:
            order_count = 0
            first_order_count = 0
            bucket_end = bucket.get_end().datetime
            # scan through the orders to find the end of the week bucket
            while pos < len(orders) and \
                    datetime.replace(orders[pos].created, tzinfo=utc) < bucket_end:
                order_count += 1
                if orders[pos].user_id not in seen:
                    first_order_count += 1
                    seen.add(orders[pos].user_id)
                pos += 1
            order_analysis.append(order_count)
            first_order_analysis.append(first_order_count)
        print(len(order_analysis), order_analysis)
        print(len(first_order_analysis), first_order_analysis)
        order_analyses.append(order_analysis)
        first_order_analyses.append(first_order_analysis)
    print(order_analyses)
    print(first_order_analyses)
    print()
