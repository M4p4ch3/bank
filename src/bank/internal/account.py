"""
Account
"""

import csv
from datetime import datetime
import logging
from typing import List

from bank.internal.statement import Statement
from bank.utils.return_code import RetCode
from bank.utils.my_date import FMT_DATE

class Account():
    """
    Account
    """

    CSV_KEY_LIST = ["id", "name"]

    def __init__(self, parent_dir: str, identifier: int, name: str) -> None:

        self.logger = logging.getLogger("Account")

        self.identifier = identifier
        self.name = name

        self.dir = f"{parent_dir}/account_{self.identifier:03}"
        self.stat_list_file_name = f"{self.dir}/statement_list.csv"

        self.stat_list: List[Statement] = []

        self.is_saved: bool = True

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

    def import_file(self) -> RetCode:
        """
        Import statement list from file
        """

        try:
            # Open statement list CSV file
            file = open(self.stat_list_file_name, "r", encoding="utf8")
        except FileNotFoundError:
            self.logger.error("open %s FAILED", self.stat_list_file_name)
            return RetCode.ERROR

        file_csv = csv.DictReader(file)

        if file_csv.fieldnames != Statement.CSV_KEY_LIST:
            self.logger.error("%s wrong CSV format", self.stat_list_file_name)

        # For each statement CSV item
        for csv_item in file_csv:

            stat_parent_dir = self.dir
            stat_id = int(csv_item["id"])
            stat_date = datetime.strptime(csv_item["date"], FMT_DATE)
            stat_bal_start = float(csv_item["bal_start"])
            stat_bal_end = float(csv_item["bal_end"])

            # Init statement
            stat = Statement(stat_parent_dir, stat_id, csv_item["name"],
                             stat_date, stat_bal_start, stat_bal_end)

            # Import statement file
            ret = stat.import_file()
            if ret != RetCode.OK:
                self.logger.error("import_file FAILED")
                return ret

            # Add statement to statements list
            self.stat_list.append(stat)

        file.close()

        return RetCode.OK

    def export_file(self) -> None:
        """
        Export statement list to file
        """

        file = open(self.stat_list_file_name, "w", encoding="utf8")

        file_csv = csv.DictWriter(file, Statement.CSV_KEY_LIST, delimiter=',', quotechar='"')

        file_csv.writeheader()

        # For each statement
        for stat in self.stat_list:

            # Create statement CSV item
            csv_item = {
                "id": str(stat.identifier),
                "date": stat.date.strftime(FMT_DATE),
                "name": stat.name,
                "bal_start": str(stat.bal_start),
                "bal_end": str(stat.bal_end)
            }

            # Write statement CSV item to file
            file_csv.writerow(csv_item)

        self.is_saved = True

        file.close()

    def add_stat(self, stat: Statement) -> None:
        """
        Add statement
        """

        # Find index
        idx = 0
        while idx < len(self.stat_list) and stat.date > self.stat_list[idx].date:
            idx = idx + 1

        # Insert statement at dedicated index
        self.stat_list.insert(idx, stat)

        self.is_saved = False

    def remove_stat(self, stat: Statement) -> None:
        """
        Remove statement
        """

        if stat not in self.stat_list:
            return

        self.stat_list.remove(stat)

        self.is_saved = False
