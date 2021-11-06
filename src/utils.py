"""
Utils
"""

from datetime import date
from enum import IntEnum
from typing import (List, Any)

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

class Clipboard():
    """
    Clipboard
    """

    def __init__(self) -> None:

        # Items list
        self.item_list: List[Any] = []

    def get_len(self) -> int:
        """
        Get items list length
        """

        return len(self.item_list)

    def clear(self) -> None:
        """
        Clean items list
        """

        if len(self.item_list) > 0:
            self.item_list.clear()

    def set(self, item_list: List[Any]) -> None:
        """
        Set items list

        Args:
            item_list (List[Any]): Items list to set in buffer
        """

        self.clear()

        for item in item_list:

            if hasattr(item, "copy"):
                # Deep copy
                item_new = item.copy()
            else:
                item_new = item

            self.item_list.append(item_new)

    def get(self) -> List[Any]:
        """
        Get items list

        Returns:
            List[Any]: Items list
        """

        return self.item_list
