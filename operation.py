
"""
Operation
"""

from datetime import datetime
from typing import Tuple

from utils import (OK, ERROR, FMT_DATE)

class Operation():
    """
    Operation
    """

    # Field index
    IDX_INVALID = -1
    IDX_DATE = 0
    IDX_MODE = 1
    IDX_TIER = 2
    IDX_CAT = 3
    IDX_DESC = 4
    IDX_AMOUNT = 5
    IDX_LAST = IDX_AMOUNT

    def __init__(self, op_date: datetime, mode: str,
                 tier: str, cat: str, desc: str, amount: float) -> None:

        self.date: datetime = op_date
        self.mode: str = mode
        self.tier: str = tier
        self.cat: str = cat
        self.desc: str = desc
        self.amount: float = amount

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

    def get_field(self, field_idx) -> Tuple[str, str]:
        """
        Get field (name, value), identified by field index
        Useful for iterating over fields
        """

        ret = ("", "")

        if field_idx == self.IDX_DATE:
            ret = ("date", self.date.strftime(FMT_DATE))
        elif field_idx == self.IDX_MODE:
            ret = ("mode", self.mode)
        elif field_idx == self.IDX_TIER:
            ret = ("tier", self.tier)
        elif field_idx == self.IDX_CAT:
            ret = ("cat", self.cat)
        elif field_idx == self.IDX_DESC:
            ret = ("desc", self.desc)
        elif field_idx == self.IDX_AMOUNT:
            ret = ("amount", str(self.amount))

        return ret

    def set_field(self, field_idx, val_str) -> int:
        """
        Set field value, identified by field index, from string
        Useful for iterating over fields
        """

        if field_idx == self.IDX_DATE:
            try:
                self.date = datetime.strptime(val_str, FMT_DATE)
            except ValueError:
                return ERROR
        elif field_idx == self.IDX_MODE:
            self.mode = val_str
        elif field_idx == self.IDX_TIER:
            self.tier = val_str
        elif field_idx == self.IDX_CAT:
            self.cat = val_str
        elif field_idx == self.IDX_DESC:
            self.desc = val_str
        elif field_idx == self.IDX_AMOUNT:
            try:
                self.amount = float(val_str)
            except ValueError:
                return ERROR

        return OK
