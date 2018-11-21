from cohort_analysis import get_bucket_for
from datetime import datetime
import dateutil


def test_get_cohort_eoy_diff():
    """In default Pacific time, midnight Dec 31 and Jan 1 UTC should be
    different ISO week buckets
    """
    assert get_bucket_for(datetime(2018, 12, 31)) \
           != get_bucket_for(datetime(2019, 1, 1))


def test_get_cohort_eoy_same():
    """In UTC buckets, midnight Dec 31 and Jan 1 UTC should be the same ISO week
    bucket
    """
    utc = dateutil.tz.gettz('UTC')
    assert get_bucket_for(datetime(2018, 12, 31), utc) \
           == get_bucket_for(datetime(2019, 1, 1), utc)
