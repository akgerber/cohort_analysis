from datetime import datetime, tzinfo
import csv
import arrow
import dateutil
from typing import Callable
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


def percent_of(of: int) -> Callable:
    """
    Enclose the printing of a percentage
    :param of: what you're taking a percentage of
    :return: a closure that prints a percentage of of
    """
    def percentage(x: int) -> str:
        return "{:.1%}".format(x/of)
    return percentage


def analyze_cohort(cohort: WeekBucket, last_order_bucket: WeekBucket) -> [str]:
    """
    Process a given weekbucket's cohort for the cohort analysis
    :param cohort:
    :param last_order_bucket:
    :return: A list of strings of analysis: the first entry is a date,
        the 2nd the # of customers, the following containing analysis by week
    """
    result = {}
    utc = dateutil.tz.gettz('UTC')
    cohort_ids = DBSERVICE.get_new_customer_ids_for(cohort)
    buckets = get_buckets_for_range(cohort, last_order_bucket)

    result["cohort"] = f"{cohort.start} - {cohort.get_end()}"
    result["customers"] = f"{len(cohort_ids)} customers"

    orders = DBSERVICE.get_orders_for(cohort_ids)
    ever_seen = set()
    pos = 0
    percent = percent_of(len(cohort_ids))

    for i in range(len(buckets)):
        bucket = buckets[i]
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
        result[f"week{i+1}"] = (f"{percent(order_count)} orderers ({order_count})\n"
            f"{percent(first_order_count)} 1st time ({first_order_count})")
    print(result)
    return result


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
    with open('analysis.csv', 'w') as csvfile:
        weekfields = [ f"week{x}" for x in list(range(1, len(cohorts) + 1))]
        fieldnames = ['cohort', 'customers'] + weekfields
        writer = csv.DictWriter(csvfile, fieldnames)
        for i in range(len(cohorts)):
            row = analyze_cohort(cohorts[i], last_order_bucket)
            writer.writerow(row)



if __name__ == "__main__":
    cohort_analysis()
