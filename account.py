
"""
Account
"""

import csv
import logging
from typing import List

from utils import (OK, ERROR)
from statement import Statement
from operation import Operation

class Account():
    """
    Account
    """

    def __init__(self) -> None:

        status: int = OK

        self.log = logging.getLogger("Account")

        self.file_path = "statements.csv"

        # Statements list
        self.stat_list: List[Statement] = list()

        # Read statements
        status = self.read()
        if status != OK:
            self.log.error("Account.__init__ ERROR : Read statements FAILED")

        # Operations buffer list
        self.op_buffer_list = list()

        self.is_unsaved: bool = False

    def get_str(self, indent: int = 0) -> str:
        """
        Get string representation
        """

        indent_str = ""
        for _ in range(indent):
            indent_str += "    "

        ret = ""
        ret += f"{indent_str}statements : [\n"
        for stat in self.stat_list:
            ret += f"{indent_str}    {{\n"
            ret += stat.get_str(indent + 2) + "\n"
            ret += f"{indent_str}    }}\n"
        ret += f"{indent_str}]"

        return ret

    def get_stat(self, stat_name: str) -> Statement:
        """
        Get statement by name
        """

        for stat in self.stat_list:
            if stat.name == stat_name:
                return stat

        return None

    def read(self) -> int:
        """
        Read from file
        """

        try:
            # Open statements CSV file
            file = open(self.file_path, "r")
        except FileNotFoundError:
            self.log.error("Account.read ERROR : Open statements CSV file FAILED")
            return ERROR

        file_csv = csv.reader(file)

        # For each statement line
        for stat_line in file_csv:

            # Create and read statement
            stat = Statement(stat_line[Statement.IDX_DATE],
                             float(stat_line[Statement.IDX_BAL_START]),
                             float(stat_line[Statement.IDX_BAL_END]))
            stat.read()

            # Add statement to statements list
            self.stat_list.append(stat)

        file.close()

        return OK

    def write(self) -> int:
        """
        Write to CSV file
        """

        try:
            # Open statements CSV file
            file = open(self.file_path, "w")
        except FileNotFoundError:
            self.log.error("Account.write ERROR : Open statements CSV file FAILED")
            return ERROR

        file_csv = csv.writer(file, delimiter=',', quotechar='"')

        # For each statement
        for stat in self.stat_list:

            # Create statement line
            stat_csv = [stat.name, str(stat.bal_start), str(stat.bal_end)]

            try:
                # Write statement line to CSV file
                file_csv.writerow(stat_csv)
            # TODO add error type
            except:
                self.log.error("Account.write ERROR : Write statement line to CSV file FAILED")
                return ERROR

        self.is_unsaved = False

        file.close()

        return OK

    def reset(self) -> int:
        """
        Reset : Read
        """

        status: int = OK

        # Read statements
        status = self.read()
        if status != OK:
            self.log.error("Account.reset ERROR : Read statements FAILED")
            return ERROR

        return OK

    def save(self) -> int:
        """
        Save : Write
        """

        status: int = OK

        # Write statements
        status = self.write()
        if status != OK:
            self.log.error("Account.save ERROR : Write statements FAILED")
            return ERROR

        return OK

    def insert_stat(self, stat: Statement) -> int:
        """
        Insert statement
        """

        # Find index
        idx = 0
        while idx < len(self.stat_list) and stat.date > self.stat_list[idx].date:
            idx = idx + 1

        # Insert statement at dedicated index
        self.stat_list.insert(idx, stat)

        self.is_unsaved = True

        return OK

    def del_stat(self, stat: Statement) -> int:
        """
        Delete statement
        """

        try:
            self.stat_list.remove(stat)
        # TODO add error type
        except:
            self.log.error("Account.del_stat ERROR : Statement not found")
            return ERROR

        self.is_unsaved = True

        return OK

    def clear_op_buffer(self) -> None:
        """
        Clear operations buffer
        """

        self.op_buffer_list.clear()

    def set_op_buffer(self, op_list: List[Operation]) -> None:
        """
        Set operations in buffer

        Args:
            op_list (List[Operation]): Operations list to set in buffer
        """

        self.clear_op_buffer()
        for op in op_list:
            # Deep copy
            op_new = op.copy()
            self.op_buffer_list.append(op_new)

    def get_op_buffer(self) -> List[Operation]:
        """
        Get operations from buffer

        Returns:
            List[Operation]: Operations in buffer
        """
        
        return self.op_buffer_list
