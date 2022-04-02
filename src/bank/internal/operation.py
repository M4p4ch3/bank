"""
Operation
"""

from datetime import datetime
from enum import IntEnum

from bank.utils import FMT_DATE

class Operation():
    """
    Operation
    """

    CSV_KEY_LIST = ["date", "mode", "tier", "cat", "desc", "amount"]

    class FieldIdx(IntEnum):
        """
        Field index
        """

        DATE = 0
        MODE = 1
        TIER = 2
        CAT = 3
        DESC = 4
        AMOUNT = 5
        LAST = AMOUNT

    def __init__(self, _date: datetime, mode: str,
                 tier: str, cat: str, desc: str, amount: float) -> None:

        self.date = _date
        self.mode = mode
        self.tier = tier
        self.cat = cat
        self.desc = desc
        self.amount = amount

    def __str__(self) -> str:

        return (f"{self.date.strftime(FMT_DATE)}, {self.mode}, {self.tier}, {self.cat}"
                f"{self.desc}, {self.amount}")

    def get_str(self, indent: int = 0) -> str:
        """
        Get string representation
        """

        indent_str = ""
        for _ in range(indent):
            indent_str += "    "

        ret = ""
        ret += f"{indent_str}date   : {self.date.strftime(FMT_DATE)}\n"
        ret += f"{indent_str}mode   : {self.mode}\n"
        ret += f"{indent_str}tier   : {self.tier}\n"
        ret += f"{indent_str}cat    : {self.cat}\n"
        ret += f"{indent_str}desc   : {self.desc}\n"
        ret += f"{indent_str}amount : {self.amount}"

        return ret

    def copy(self):
        """
        Deep copy : Create and return new operation

        Returns:
            Operation: Created deep copy
        """

        return Operation(self.date, self.mode, self.tier, self.cat, self.desc, self.amount)
