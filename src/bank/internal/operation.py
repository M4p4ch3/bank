"""
bank/internal/operation
"""

from datetime import datetime
from enum import IntEnum
import logging
from typing import Tuple

from bank.internal.item import Item
from bank.utils.my_date import FMT_DATE
from bank.utils.return_code import RetCode

class Operation(Item):
    """
    Operation
    """

    # CSV row key list
    KEY_LIST = ["date", "mode", "tier", "cat", "desc", "amount"]

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

    def __init__(self) -> None:

        super().__init__()

        self.logger = logging.getLogger("Operation")

        self.date: datetime = None
        self.mode: str = ""
        self.tier: str = ""
        self.cat: str = ""
        self.desc: str = ""
        self.amount: float = 0.0

    def to_string(self, indent: int = 0) -> str:
        """
        To string

        Args:
            indent (int): Indentation level

        Returns:
            str: String
        """

        indent_str = ""
        for _ in range(indent):
            indent_str += "    "

        ret = ""
        ret += f"{indent_str}date : {self.date.strftime(FMT_DATE)}\n"
        ret += f"{indent_str}mode : {self.mode}\n"
        ret += f"{indent_str}tier : {self.tier}\n"
        ret += f"{indent_str}cat : {self.cat}\n"
        ret += f"{indent_str}desc : {self.desc}\n"
        ret += f"{indent_str}amount : {self.amount}"

        return ret

    def update_from_csv(self, row: dict) -> RetCode:
        """
        Update item from CSV row dict

        Args:
            row (dict): CSV row dict
        """

        for key in self.KEY_LIST:
            if key not in row:
                self.logger.error("update_from_csv : Key %s not in CSV row", key)
                return RetCode.ERROR

        try:
            self.date = datetime.strptime(row["date"], FMT_DATE)
        except ValueError:
            self.logger.error("update_from_csv : Convert %s to date FAILED", row["date"])
            return RetCode.ERROR

        self.mode = row["mode"]
        self.tier = row["tier"]
        self.cat = row["cat"]
        self.desc = row["desc"]

        try:
            self.amount = float(row["amount"])
        except ValueError:
            self.logger.error("update_from_csv : Convert %s to float FAILED", row["amount"])
            return RetCode.ERROR

        return RetCode.OK

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
