"""
Account
"""

import csv
import logging
from typing import List

from .statement import Statement

class Account():
    """
    Account
    """

    def __init__(self) -> None:

        self.logger = logging.getLogger("Account")

        self.file_path = "./data/statements.csv"

        # Statements list
        self.stat_list: List[Statement] = list()

        # Import statements from file
        self.import_file()

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

    def import_file(self) -> None:
        """
        Import statements from file
        """

        try:
            # Open statements CSV file
            file = open(self.file_path, "r", encoding="utf8")
        except FileNotFoundError:
            self.logger.error("Account.import_file ERROR : Open statements CSV file FAILED")
            return

        file_csv = csv.reader(file)

        # For each statement line
        for stat_line in file_csv:

            # Create statement
            stat = Statement(stat_line[Statement.IDX_DATE],
                             float(stat_line[Statement.IDX_BAL_START]),
                             float(stat_line[Statement.IDX_BAL_END]))

            # Add statement to statements list
            self.stat_list.append(stat)

        file.close()

    def export_file(self):
        """
        Export statements to file
        """

        try:
            # Open statements CSV file
            file = open(self.file_path, "w", encoding="utf8")
        except FileNotFoundError:
            self.logger.error("Account.export_file ERROR : Open statements CSV file FAILED")
            return

        file_csv = csv.writer(file, delimiter=',', quotechar='"')

        # For each statement
        for stat in self.stat_list:

            # Create statement line
            stat_csv = [stat.name, str(stat.bal_start), str(stat.bal_end)]

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
