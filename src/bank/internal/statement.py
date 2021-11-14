"""
bank/internal/statement
"""

import csv
from datetime import datetime
from enum import IntEnum
import logging
from typing import (List, Tuple)

from bank.internal.operation import Operation
from bank.internal.container import Container
from bank.internal.item import Item
from bank.utils.return_code import RetCode
from bank.utils.my_date import FMT_DATE

class Statement(Container, Item):
    """
    Statement
    """

    # CSV row key list
    KEY_LIST = ["date", "bal_start", "bal_end"]

    class FieldIdx(IntEnum):
        """
        Field index
        """

        DATE = 0
        BAL_START = 1
        BAL_END = 2
        LAST = BAL_END

    def __init__(self, name: str, dir_path: str) -> None:

        Container.__init__(self, name, dir_path, "operations")

        self.logger = logging.getLogger("Statement")

        self.date: datetime = None
        self.bal_start: float = 0.0
        self.bal_end: float = 0.0
        self.op_sum: float = 0.0

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

        # Item
        ret += f"{indent_str}file : {self.file_path}\n"
        ret += f"{indent_str}date : {self.date.strftime(FMT_DATE)}\n"
        ret += f"{indent_str}balance start : {str(self.bal_start)}\n"
        ret += f"{indent_str}balance end : {str(self.bal_end)}\n"
        ret += f"{indent_str}balance diff : {str(self.bal_end - self.bal_start)}\n"
        ret += f"{indent_str}operations sum : {str(self.op_sum)}\n"
        ret += f"{indent_str}balance error : {str(self.op_sum - self.bal_end + self.bal_start)}\n"

        # Container
        ret += Container.to_string(self, indent=(indent + 1))

        return ret

    def init_item(self) -> Item:
        """
        Init item

        Returns:
            Item: Item
        """

        operation = Operation()
        return operation

    def add_item(self, item: Item) -> None:
        """
        Add item to list

        Args:
            item (Item): Item
        """

        Container.add_item(self, item)

        self.op_sum += item.amount

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

        date_str = row["date"]

        try:
            self.date = datetime.strptime(row["date"], FMT_DATE)
        except ValueError:
            self.logger.error("update_from_csv : Convert %s to date FAILED", row["date"])
            return RetCode.ERROR

        self.bal_start = float(row["bal_start"])
        self.bal_end = float(row["bal_end"])

        # Item
        self.key = self.date

        # Container
        self.name = "statement_" + date_str
        self.file_path = self.dir_path + "/" + date_str + ".csv"

        # Now ready to import file
        ret = self.import_file()
        if ret != RetCode.OK:
            self.logger.error("update_from_csv : Import file of %s FAILED", self.name)
            return ret

        return RetCode.OK

    # def get_field(self, field_idx: int) -> Tuple[str, str]:
    #     """
    #     Get field (name, value), identified by field index
    #     Useful for iterating over fields
    #     """

    #     ret = ("", "")
    #     if field_idx == self.FieldIdx.DATE:
    #         ret = ("date", self.date.strftime(FMT_DATE))
    #     elif field_idx == self.FieldIdx.BAL_START:
    #         ret = ("start balance", str(self.bal_start))
    #     elif field_idx == self.FieldIdx.BAL_END:
    #         ret = ("start balance", str(self.bal_end))

    #     return ret

    # def get_closest_op(self, item_list: List[Operation]) -> Operation:
    #     """
    #     Get closest operation from list
    #     None if not found
    #     """

    #     # Operation to return
    #     op_ret: Operation = item_list[0]

    #     # While operation in list
    #     while (op_ret in item_list) and (op_ret is not None):

    #         # Get operation index in statement
    #         op_ret_idx = self.item_list.index(op_ret)

    #         # If first operation in list is first operation in statement
    #         if self.item_list.index(item_list[0]) == 0:
    #             # Search forward
    #             op_ret_idx = op_ret_idx + 1
    #         # Else, first operation in list is not first one
    #         else:
    #             # Search backward
    #             op_ret_idx = op_ret_idx - 1

    #         # If operation out of statement
    #         if op_ret_idx < 0 or op_ret_idx >= len(self.item_list):
    #             op_ret = None
    #         else:
    #             op_ret = self.item_list[op_ret_idx]

    #     return op_ret

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
    #     elif field_idx == self.FieldIdx.BAL_START:
    #         try:
    #             self.bal_start = float(val_str)
    #         except ValueError:
    #             is_edited = False
    #     elif field_idx == self.FieldIdx.BAL_END:
    #         try:
    #             self.bal_end = float(val_str)
    #         except ValueError:
    #             is_edited = False

    #     if is_edited:
    #         self.is_saved = False

    #     return is_edited

    # def create_file(self) -> RetCode:
    #     """
    #     Create file
    #     """

    #     try:
    #         file = open(self.file_path, "w+", encoding="utf8")
    #     except OSError:
    #         self.logger.error("create_file : Open %s file FAILED", self.file_path)
    #         return RetCode.ERROR

    #     file.close()

    #     return RetCode.OK

    # def import_file(self) -> RetCode:
    #     """
    #     Import operations from file
    #     """

    #     try:
    #         # Open CSV file
    #         file = open(self.file_path, "r", encoding="utf8")
    #     except FileNotFoundError:
    #         self.logger.error("import_file : Open %s file FAILED", self.file_path)
    #         return RetCode.ERROR

    #     file_csv = csv.reader(file)

    #     # Clear operations list
    #     self.item_list.clear()
    #     # Reset operations sum
    #     self.op_sum = 0.0

    #     # For each operation line in statement CSV file
    #     for op_line in file_csv:

    #         # Create operation
    #         op_date = datetime.strptime(op_line[Operation.FieldIdx.DATE], FMT_DATE)
    #         operation = Operation(
    #             op_date, op_line[Operation.FieldIdx.MODE], op_line[Operation.FieldIdx.TIER],
    #             op_line[Operation.FieldIdx.CAT], op_line[Operation.FieldIdx.DESC],
    #             float(op_line[Operation.FieldIdx.AMOUNT]))

    #         # Add operation to list
    #         self.item_list.append(operation)

    #         # Update operations sum
    #         self.op_sum = self.op_sum + operation.amount

    #     self.is_saved = True

    #     file.close()

    #     return RetCode.OK

    # def export_file(self) -> None:
    #     """
    #     Export operations to file
    #     """

    #     # Open CSV file
    #     file = open(self.file_path, "w", encoding="utf8")

    #     file_csv = csv.writer(file, delimiter=',', quotechar='"')

    #     # For each operation
    #     for operation in self.item_list:

    #         # Create operation line
    #         op_csv = [operation.date.strftime(FMT_DATE), operation.mode, operation.tier,
    #                   operation.cat, operation.desc, str(operation.amount)]

    #         # Write operation line to CSV file
    #         file_csv.writerow(op_csv)

    #     self.is_saved = True

    #     file.close()

    # def add_op(self, operation: Operation) -> None:
    #     """
    #     Add operation
    #     """

    #     # Find index
    #     idx = 0
    #     while idx < len(self.item_list) and operation.date > self.item_list[idx].date:
    #         idx = idx + 1

    #     # Insert operation at dedicated index
    #     self.item_list.insert(idx, operation)

    #     # Update operation sum
    #     self.op_sum += operation.amount

    #     self.is_saved = False

    # def remove_op(self, operation: Operation) -> None:
    #     """
    #     Remove operation
    #     """

    #     if operation not in self.item_list:
    #         return

    #     self.item_list.remove(operation)

    #     self.op_sum -= operation.amount

    #     self.is_saved = False

    # def remove_item_list(self, item_list: List[Operation]) -> None:
    #     """
    #     Remove operation list
    #     """

    #     for operation in item_list:
    #         self.remove_op(operation)
