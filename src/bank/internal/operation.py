"""
Operation
"""

from datetime import datetime
from enum import IntEnum
from typing import Tuple

from bank.utils import FMT_DATE

class Operation():
    """
    Operation
    """

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

    def __init__(self, op_date: datetime, mode: str,
                 tier: str, cat: str, desc: str, amount: float) -> None:

        self.date = op_date
        self.mode = mode
        self.tier = tier
        self.cat = cat
        self.desc = desc
        self.amount = amount

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

    # def get_field(self, field_idx) -> Tuple[str, str]:
    #     """
    #     Get field (name, value), identified by field index
    #     Useful for iterating over fields
    #     """

    #     ret = ("", "")

    #     if field_idx == self.FieldIdx.DATE:
    #         ret = ("date", self.date.strftime(FMT_DATE))
    #     elif field_idx == self.FieldIdx.MODE:
    #         ret = ("mode", self.mode)
    #     elif field_idx == self.FieldIdx.TIER:
    #         ret = ("tier", self.tier)
    #     elif field_idx == self.FieldIdx.CAT:
    #         ret = ("cat", self.cat)
    #     elif field_idx == self.FieldIdx.DESC:
    #         ret = ("desc", self.desc)
    #     elif field_idx == self.FieldIdx.AMOUNT:
    #         ret = ("amount", str(self.amount))

    #     return ret

    # def set_field(self, field_idx, val_str) -> bool:
    #     """
    #     Set field value, identified by field index, from string
    #     Useful for iterating over fields
    #     """

    #     is_edited = True

    #     if field_idx == self.FieldIdx.DATE:
    #         try:
    #             self.date = datetime.strptime(val_str, FMT_DATE)
    #         except ValueError:
    #             is_edited = False
    #     elif field_idx == self.FieldIdx.MODE:
    #         self.mode = val_str
    #     elif field_idx == self.FieldIdx.TIER:
    #         self.tier = val_str
    #     elif field_idx == self.FieldIdx.CAT:
    #         self.cat = val_str
    #     elif field_idx == self.FieldIdx.DESC:
    #         self.desc = val_str
    #     elif field_idx == self.FieldIdx.AMOUNT:
    #         try:
    #             self.amount = float(val_str)
    #         except ValueError:
    #             is_edited = False

    #     return is_edited

    def copy(self):
        """
        Deep copy : Create and return new operation

        Returns:
            Operation: Created deep copy
        """

        return Operation(self.date, self.mode, self.tier, self.cat, self.desc, self.amount)
