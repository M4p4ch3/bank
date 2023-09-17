"""
Statement
"""

import csv
from datetime import datetime
from enum import IntEnum
import logging
import os
from typing import (List, Tuple)

from bank.internal.operation import Operation
from bank.utils.return_code import RetCode
from bank.utils.my_date import FMT_DATE

class Statement():
    """
    Statement
    """

    CSV_KEY_LIST = ["id", "name", "date", "bal_start", "bal_end"]

    class FieldIdx(IntEnum):
        """
        Field index
        """

        DATE = 0
        BAL_START = 1
        BAL_END = 2
        LAST = BAL_END

    def __init__(self, parent_dir: str, identifier: int, name: str,
                 date: datetime, bal_start: float, bal_end: float) -> None:

        self.logger = logging.getLogger("Statement")

        self.identifier = identifier
        self.name = name

        self.date = date
        self.bal_start = bal_start
        self.bal_end = bal_end

        self.dir = f"{parent_dir}/statement_{self.identifier:03}"
        self.op_list_file_name = f"{self.dir}/operation_list.csv"

        self.op_sum: float = 0.0
        self.op_list: List[Operation] = []

        self.is_saved: bool = True

    def get_str(self, indent: int = 0) -> str:
        """
        Get string representation
        """

        indent_str = ""
        for _ in range(indent):
            indent_str += "    "

        ret = ""
        ret += f"{indent_str}date : {self.date.strftime(FMT_DATE)}\n"
        ret += f"{indent_str}balance : [{str(self.bal_start)}, {str(self.bal_end)}]\n"
        ret += f"{indent_str}operations sum : {str(self.op_sum)}\n"
        ret += f"{indent_str}balance diff : {str(self.op_sum - self.bal_end)}\n"
        ret += f"{indent_str}operations : [\n"
        for operation in self.op_list:
            ret += f"{indent_str}    {{\n"
            ret += operation.get_str(indent + 2) + "\n"
            ret += f"{indent_str}    }}\n"
        ret += f"{indent_str}]"

        return ret

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

    def get_closest_op(self, op_list: List[Operation]) -> Operation:
        """
        Get closest operation from list
        None if not found
        """

        # Operation to return
        op_ret: Operation = op_list[0]

        # While operation in list
        while (op_ret in op_list) and (op_ret is not None):

            # Get operation index in statement
            op_ret_idx = self.op_list.index(op_ret)

            # If first operation in list is first operation in statement
            if self.op_list.index(op_list[0]) == 0:
                # Search forward
                op_ret_idx = op_ret_idx + 1
            # Else, first operation in list is not first one
            else:
                # Search backward
                op_ret_idx = op_ret_idx - 1

            # If operation out of statement
            if op_ret_idx < 0 or op_ret_idx >= len(self.op_list):
                op_ret = None
            else:
                op_ret = self.op_list[op_ret_idx]

        return op_ret

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

    def import_file(self) -> RetCode:
        """
        Import operation list from file
        """

        try:
            # Open CSV file
            file = open(self.op_list_file_name, "r", encoding="utf8")
        except FileNotFoundError:
            self.logger.error("open %s FAILED", self.op_list_file_name)
            return RetCode.ERROR

        file_csv = csv.DictReader(file)

        # Strip last CSV field if empty
        if file_csv.fieldnames[len(file_csv.fieldnames) - 1] == "":
            file_csv.fieldnames = file_csv.fieldnames[:-1]

        # Check CSV fields match operation ones
        if file_csv.fieldnames != Operation.CSV_KEY_LIST:
            self.logger.error("%s wrong CSV format", self.op_list_file_name)

        # Clear operations list
        self.op_list.clear()
        # Reset operations sum
        self.op_sum = 0.0

        # For each operation CSV item
        for csv_item in file_csv:

            # Create operation
            op_date = datetime.strptime(csv_item["date"], FMT_DATE)
            operation = Operation(
                op_date, csv_item["mode"], csv_item["tier"],
                csv_item["cat"], csv_item["desc"],
                float(csv_item["amount"]))

            # Add operation to list
            self.op_list.append(operation)

            # Update operations sum
            self.op_sum = self.op_sum + operation.amount

        self.is_saved = True

        file.close()

        return RetCode.OK

    def export_file(self) -> None:
        """
        Export operation list to file
        """

        # If file directory does not exist
        if not os.path.exists(os.path.dirname(self.op_list_file_name)):
            # Create file directory
            os.makedirs(os.path.dirname(self.op_list_file_name))

        file = open(self.op_list_file_name, "w", encoding="utf8")

        file_csv = csv.DictWriter(file, Operation.CSV_KEY_LIST, delimiter=',', quotechar='"')

        file_csv.writeheader()

        # For each operation
        for operation in self.op_list:

            # Create operation CSV item
            csv_item = {
                "date": operation.date.strftime(FMT_DATE),
                "mode": operation.mode,
                "tier": operation.tier,
                "cat": operation.cat,
                "desc": operation.desc,
                "amount": str(operation.amount),
            }

            # Write operation CSV item to file
            file_csv.writerow(csv_item)

        self.is_saved = True

        file.close()

    def add_op(self, operation: Operation) -> None:
        """
        Add operation
        """

        # Find index
        idx = 0
        while idx < len(self.op_list) and operation.date > self.op_list[idx].date:
            idx = idx + 1

        # Insert operation at dedicated index
        self.op_list.insert(idx, operation)

        # Update operation sum
        self.op_sum += operation.amount

        self.is_saved = False

    def remove_op(self, operation: Operation) -> None:
        """
        Remove operation
        """

        if operation not in self.op_list:
            return

        self.op_list.remove(operation)

        self.op_sum -= operation.amount

        self.is_saved = False

    def remove_op_list(self, op_list: List[Operation]) -> None:
        """
        Remove operation list
        """

        for operation in op_list:
            self.remove_op(operation)
