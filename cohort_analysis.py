"""
Script to execute a cohort analysis
"""
from datetime import datetime, tzinfo
from typing import Callable
import csv
import logging

import arrow
import dateutil

from models import WeekBucket
from service import DBSERVICE

ANALYSIS_FILE = 'analysis.csv'


def get_bucket_for(date_time: datetime,
                   timezone: tzinfo = dateutil.tz.gettz('US/Pacific'))\
        -> WeekBucket:
    """
    Place a datetime in a weeklong cohort (with weeks starting/ending in the specified timezone)
    :param date_time: a datetime
    :param timezone: the timezone used to determine week boundaries
    :return: a Cohort including the datetime
    """
    # use Arrow library as builtin datetime doesn't support DST changing over time
    as_tz = arrow.get(date_time).to(timezone)
    iso = as_tz.isocalendar()
    cohort_start = arrow.Arrow.strptime(f"{iso[0]}|{iso[1]}" +"|1", "%G|%V|%u", timezone)
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


def percent_of(of_what: int) -> Callable:
    """
    Enclose the printing of a percentage
    :param of_what: what you're taking a percentage of
    :return: a closure that prints a percentage of of
    """
    def percentage(x: int) -> str:
        return "{:.1%}".format(x / of_what)
    return percentage


def analyze_cohort(cohort: WeekBucket, last_order_bucket: WeekBucket) \
        -> {str: str}:
    """
    Process a given weekbucket's cohort for the cohort analysis
    :param cohort:
    :param last_order_bucket:
    :return: A dictionary of strings of analysis
    """
    result = {}
    utc = dateutil.tz.gettz('UTC')
    cohort_ids = DBSERVICE.get_new_customer_ids_for(cohort)
    buckets = get_buckets_for_range(cohort, last_order_bucket)

    result["Cohort"] = f"{cohort.start} - {cohort.get_end()}"
    result["Customers"] = f"{len(cohort_ids)} customers"

    orders = DBSERVICE.get_orders_for(cohort_ids)
    ever_seen = set()
    pos = 0
    percent = percent_of(len(cohort_ids))

    for i, bucket in enumerate(buckets):
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
        week = f"{i*7}-{(i+1)*7-1} days"
        result[week] = (f"{percent(order_count)} orderers ({order_count})\n"
                        f"{percent(first_order_count)} "
                        f"1st time ({first_order_count})")
    return result


def cohort_analysis():
    """
    Do a cohort analysis
    :return:
    """
    DBSERVICE.logger.setLevel(logging.INFO)
    start = DBSERVICE.get_oldest_customer_date()
    end = DBSERVICE.get_newest_customer_date()
    order_end = DBSERVICE.get_newest_order_date()
    first_cohort = get_bucket_for(start)
    last_cohort = get_bucket_for(end)
    last_order_bucket = get_bucket_for(order_end)
    cohorts = get_buckets_for_range(first_cohort, last_cohort)
    with open(ANALYSIS_FILE, 'w') as csvfile:
        weekfields = \
            [f"{i*7}-{(i+1)*7-1} days" for i in list(range(0, len(cohorts)))]
        fieldnames = ['Cohort', 'Customers'] + weekfields
        writer = csv.DictWriter(csvfile, fieldnames)
        writer.writeheader()
        for i in range(len(cohorts)-1, -1, -1):
            row = analyze_cohort(cohorts[i], last_order_bucket)
            writer.writerow(row)
    DBSERVICE.logger.info("Writing analysis to %s", ANALYSIS_FILE)


if __name__ == "__main__":
    DBSERVICE.import_all_data()
    cohort_analysis()
