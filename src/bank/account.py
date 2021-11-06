"""
Account
"""

import csv
from datetime import datetime
import logging
from typing import List

from .statement import Statement
from .utils.error_code import (OK, ERROR)
from .utils.my_date import FMT_DATE

class Account():
    """
    Account
    """

    def __init__(self) -> None:

        self.logger = logging.getLogger("Account")

        self.file_path = "./data/statements.csv"

        # Statements list
        self.stat_list: List[Statement] = list()

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

    def get_stat(self, date: datetime) -> Statement:
        """
        Get statement by date
        """

        for stat in self.stat_list:
            if stat.date == date:
                return stat

        return None

    def import_file(self) -> int:
        """
        Import statements from file
        """

        try:
            # Open statements CSV file
            file = open(self.file_path, "r", encoding="utf8")
        except FileNotFoundError:
            self.logger.error("import_file : Open %s file FAILED", self.file_path)
            return ERROR

        file_csv = csv.reader(file)

        # For each statement line
        for stat_line in file_csv:

            # Init statement
            stat = Statement(stat_line[Statement.IDX_DATE],
                             float(stat_line[Statement.IDX_BAL_START]),
                             float(stat_line[Statement.IDX_BAL_END]))

            # Import statement file
            ret = stat.import_file()
            if ret != OK:
                self.logger.error("import_file : Import statement file FAILED")
                return ret

            # Add statement to statements list
            self.stat_list.append(stat)

        file.close()

        return OK

    def export_file(self):
        """
        Export statements to file
        """

        try:
            # Open statements CSV file
            file = open(self.file_path, "w", encoding="utf8")
        except FileNotFoundError:
            self.logger.error("export_file : Open %s file FAILED", self.file_path)
            return

        file_csv = csv.writer(file, delimiter=',', quotechar='"')

        # For each statement
        for stat in self.stat_list:

            # Create statement line
            stat_csv = [stat.date.strftime(FMT_DATE),
                        str(stat.bal_start), str(stat.bal_end)]

            # Write statement line to CSV file
            file_csv.writerow(stat_csv)

        self.is_unsaved = False

        file.close()

    def insert_stat(self, stat: Statement) -> None:
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

    def del_stat(self, stat: Statement) -> None:
        """
        Delete statement
        """

        if stat not in self.stat_list:
            return

        self.stat_list.remove(stat)

        self.is_unsaved = True
