from datetime import datetime, tzinfo
import dateutil
import arrow
from models import WeekBucket
from service import DBSERVICE


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
    """
    Get a range of WeekBuckets between first and last
    :param first: the start of the range
    :param last: the end of the range
    :return: WeekBuckets from first to last
    """
    bucket_range = [first]
    while first != last:
        first = get_bucket_for(first.get_end())
        bucket_range.append(first)
    return bucket_range


def cohort_analysis():
    """
    Do a cohort analysis
    :return:
    """
    start = DBSERVICE.get_oldest_customer_date()
    end = DBSERVICE.get_newest_customer_date()
    order_end = DBSERVICE.get_newest_order_date()
    first_cohort = get_bucket_for(start)
    last_cohort = get_bucket_for(end)
    last_order_bucket = get_bucket_for(order_end)
    cohorts = get_buckets_for_range(first_cohort, last_cohort)
    for cohort in cohorts:
        process_cohort(cohort, last_order_bucket)


def process_cohort(cohort: WeekBucket, last_order_bucket: WeekBucket):
    utc = dateutil.tz.gettz('UTC')
    cohort_ids = DBSERVICE.get_new_customer_ids_for(cohort)
    buckets = get_buckets_for_range(cohort, last_order_bucket)
    order_analysis = []
    first_order_analysis = []
    orders = DBSERVICE.get_orders_for(cohort_ids)
    ever_seen = set()
    pos = 0
    for bucket in buckets:
        order_count = 0
        first_order_count = 0
        bucket_seen = set()
        bucket_end = bucket.get_end().datetime
        # scan through the orders to find the end of the week bucket
        while pos < len(orders) and \
                datetime.replace(orders[pos].created, tzinfo=utc) < bucket_end:
            if orders[pos].user_id not in bucket_seen:
                order_count += 1
                bucket_seen.add(orders[pos].user_id)
            if orders[pos].user_id not in ever_seen:
                first_order_count += 1
                ever_seen.add(orders[pos].user_id)
            pos += 1
        order_analysis.append(order_count)
        first_order_analysis.append(first_order_count)
    size = len(cohort_ids)
    percent = lambda x: "{:.1%}".format(x/size)
    print(size)
    print(len(order_analysis), order_analysis)
    print(len(order_analysis), list(map(percent, order_analysis)))
    print(len(first_order_analysis), first_order_analysis)
    print(len(first_order_analysis), list(map(percent, first_order_analysis)))


if __name__ == "__main__":
    cohort_analysis()
