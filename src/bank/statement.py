"""
Statement
"""

import csv
from datetime import datetime
from enum import IntEnum
import logging
from typing import (List, Tuple)

from .operation import Operation
from .utils.return_code import RetCode
from .utils.my_date import FMT_DATE

class Statement():
    """
    Statement
    """

    class FieldIdx(IntEnum):
        """
        Field index
        """

        DATE = 0
        BAL_START = 1
        BAL_END = 2
        LAST = BAL_END

    def __init__(self, date_str: str, bal_start: float, bal_end: float) -> None:

        self.logger = logging.getLogger("Statement")

        self.file_path: str = f"./data/statements/{date_str}.csv"

        try:
            self.date: datetime = datetime.strptime(date_str, FMT_DATE)
        except ValueError:
            # For pending statement
            self.date: datetime = datetime.now()

        self.bal_start: float = bal_start
        self.bal_end: float = bal_end
        self.op_sum: float = 0.0
        self.op_list: List[Operation] = list()

        self.is_unsaved: bool = False

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

    def get_field(self, field_idx: int) -> Tuple[str, str]:
        """
        Get field (name, value), identified by field index
        Useful for iterating over fields
        """

        ret = ("", "")
        if field_idx == self.FieldIdx.DATE:
            ret = ("date", self.date.strftime(FMT_DATE))
        elif field_idx == self.FieldIdx.BAL_START:
            ret = ("start balance", str(self.bal_start))
        elif field_idx == self.FieldIdx.BAL_END:
            ret = ("start balance", str(self.bal_end))

        return ret

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

    def set_field(self, field_idx, val_str) -> bool:
        """
        Set field value, identified by field index, from string
        Useful for iterating over fields
        """

        is_edited = True

        if field_idx == self.FieldIdx.DATE:
            try:
                self.date = datetime.strptime(val_str, FMT_DATE)
            except ValueError:
                is_edited = False
        elif field_idx == self.FieldIdx.BAL_START:
            try:
                self.bal_start = float(val_str)
            except ValueError:
                is_edited = False
        elif field_idx == self.FieldIdx.BAL_END:
            try:
                self.bal_end = float(val_str)
            except ValueError:
                is_edited = False

        if is_edited:
            self.is_unsaved = True

        return is_edited

    def create_file(self) -> RetCode:
        """
        Create file
        """

        try:
            file = open(self.file_path, "w+", encoding="utf8")
        except OSError:
            self.logger.error("create_file : Open %s file FAILED", self.file_path)
            return RetCode.ERROR

        file.close()

        return RetCode.OK

    def import_file(self) -> RetCode:
        """
        Import operations from file
        """

        try:
            # Open CSV file
            file = open(self.file_path, "r", encoding="utf8")
        except FileNotFoundError:
            self.logger.error("import_file : Open %s file FAILED", self.file_path)
            return RetCode.ERROR

        file_csv = csv.reader(file)

        # Clear operations list
        self.op_list.clear()
        # Reset operations sum
        self.op_sum = 0.0

        # For each operation line in statement CSV file
        for op_line in file_csv:

            # Create operation
            op_date = datetime.strptime(op_line[Operation.FieldIdx.DATE], FMT_DATE)
            operation = Operation(
                op_date, op_line[Operation.FieldIdx.MODE], op_line[Operation.FieldIdx.TIER],
                op_line[Operation.FieldIdx.CAT], op_line[Operation.FieldIdx.DESC],
                float(op_line[Operation.FieldIdx.AMOUNT]))

            # Add operation to list
            self.op_list.append(operation)

            # Update operations sum
            self.op_sum = self.op_sum + operation.amount

        self.is_unsaved = False

        file.close()

        return RetCode.OK

    def export_file(self) -> None:
        """
        Export operations to file
        """

        # Open CSV file
        file = open(self.file_path, "w", encoding="utf8")

        file_csv = csv.writer(file, delimiter=',', quotechar='"')

        # For each operation
        for operation in self.op_list:

            # Create operation line
            op_csv = [operation.date.strftime(FMT_DATE), operation.mode, operation.tier,
                      operation.cat, operation.desc, str(operation.amount)]

            # Write operation line to CSV file
            file_csv.writerow(op_csv)

        self.is_unsaved = False

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

        self.is_unsaved = True

    def remove_op(self, operation: Operation) -> None:
        """
        Remove operation
        """

        if operation not in self.op_list:
            return

        self.op_list.remove(operation)

        self.op_sum -= operation.amount

        self.is_unsaved = True

    def remove_op_list(self, op_list: List[Operation]) -> None:
        """
        Remove operation list
        """

        for operation in op_list:
            self.remove_op(operation)
