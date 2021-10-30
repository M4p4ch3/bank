"""
Utils
"""

from datetime import date
from enum import IntEnum
from typing import List

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

class ColorPairId(IntEnum):
    """
    Curses color pair ID
    """

    RED_BLACK = 1
    GREEN_BLACK = 2

class WinId(IntEnum):
    """
    Window ID
    """

    MAIN = 0
    SUB = 1
    INFO = 2
    INPUT = 3
    # CMD = 4
    # STATUS = 5
    LAST = INPUT

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

class ObjListBuffer():
    """
    Objects list buffer
    """

    def __init__(self) -> None:

        self.obj_list: List = []

    def clear(self) -> None:
        """
        Clear objects buffer
        """

        if len(self.obj_list) > 0:
            self.obj_list.clear()

    def set(self, obj_list: List) -> None:
        """
        Set objects in buffer

        Args:
            obj_list (List): objects list to set in buffer
        """

        self.clear()

        for operation in obj_list:

            # Deep copy
            op_new = operation.copy()

            self.obj_list.append(op_new)

    def get(self) -> List:
        """
        Get objects from buffer

        Returns:
            List: objects in buffer
        """

        return self.obj_list
