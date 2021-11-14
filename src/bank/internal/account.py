"""
bank/internal/account
"""

import csv
from datetime import datetime
import logging
from typing import List

from bank.internal.statement import Statement
from bank.internal.container import Container
from bank.internal.item import Item
from bank.utils.return_code import RetCode
from bank.utils.my_date import FMT_DATE

class Account(Container):
    """
    Account
    """

    def __init__(self, name: str, dir_path: str) -> None:

        Container.__init__(self, name, dir_path, "statements")
        # Item.__init__()

        self.logger = logging.getLogger("Account")

    def to_string(self, indent: int = 0) -> str:
        """
        To string

        Args:
            indent (int): Indentation level

        Returns:
            str: String
        """

        # indent_str = ""
        # for _ in range(indent):
        #     indent_str += "    "

        ret = ""
        # ret += f"{indent_str}custom"
        ret += Container.to_string(self, indent=indent)

        return ret

    def init_item(self) -> Item:
        """
        Init item

        Returns:
            Item: Item
        """

        dir_path = self.dir_path + "/statements/"
        stat = Statement("", dir_path)
        return stat

    # def get_stat(self, date: datetime) -> Statement:
    #     """
    #     Get statement by date
    #     """

    #     for stat in self.item_list:
    #         if stat.date == date:
    #             return stat

    #     return None

    # def export_file(self):
    #     """
    #     Export statements to file
    #     """

    #     try:
    #         # Open statements CSV file
    #         file = open(self.file_path, "w", encoding="utf8")
    #     except FileNotFoundError:
    #         self.logger.error("export_file : Open %s file FAILED", self.file_path)
    #         return

    #     file_csv = csv.writer(file, delimiter=',', quotechar='"')

    #     # For each statement
    #     for stat in self.item_list:

    #         # Create statement line
    #         stat_csv = [stat.date.strftime(FMT_DATE),
    #                     str(stat.bal_start), str(stat.bal_end)]

    #         # Write statement line to CSV file
    #         file_csv.writerow(stat_csv)

    #     self.is_saved = True

    #     file.close()

    # def add_stat(self, stat: Statement) -> None:
    #     """
    #     Add statement
    #     """

    #     # Find index
    #     idx = 0
    #     while idx < len(self.item_list) and stat.date > self.item_list[idx].date:
    #         idx = idx + 1

    #     # Insert statement at dedicated index
    #     self.item_list.insert(idx, stat)

    #     self.is_saved = False

    # def remove_stat(self, stat: Statement) -> None:
    #     """
    #     Remove statement
    #     """

    #     if stat not in self.item_list:
    #         return

    #     self.item_list.remove(stat)

    #     self.is_saved = False
