
from datetime import date

# Return code
OK = 0
ERROR = 1

# Length for display padding
LEN_DATE = 10
LEN_NAME = LEN_DATE
LEN_TYPE = 8
LEN_TIER = 18
LEN_CAT = 10
LEN_DESC = 35
LEN_AMOUNT = 8

# datetime date format
FMT_DATE = "%Y-%m-%d"

# Get next month of date
def getNextMonth(inDate: date):

    if inDate.month == 12:
        outDate = date(inDate.year + 1, 1, inDate.day)
    else:
        outDate = date(inDate.year, inDate.month + 1, inDate.day)

    return outDate
