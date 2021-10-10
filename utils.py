
"""
Utils
"""

from datetime import date

# Return code
OK = 0
ERROR = 1

# Length for display padding
LEN_DATE = 10
LEN_NAME = LEN_DATE
LEN_MODE = 8
LEN_TIER = 18
LEN_CAT = 10
LEN_DESC = 35
LEN_AMOUNT = 8

# datetime date format
FMT_DATE = "%Y-%m-%d"

# Get next month of date
def get_next_month(date_in: date):
    """
    Get next month from date
    """

    if date_in.month == 12:
        date_ret = date(date_in.year + 1, 1, date_in.day)
    else:
        date_ret = date(date_in.year, date_in.month + 1, date_in.day)

    return date_ret
