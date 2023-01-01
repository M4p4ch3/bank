"""
Statement
"""

import csv
from datetime import datetime
from enum import IntEnum
import json
import logging
import os
from typing import List

from bank.internal.operation import Operation
from bank.utils.my_date import FMT_DATE

# pylint: disable=too-many-instance-attributes
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
        NAME = 1
        BAL_START = 2
        BAL_END = 3
        LAST = BAL_END

    def __init__(self, parent_dir: str, name: str = "") -> None:

        self.logger = logging.getLogger("Statement")

        self.parent_dir: str = parent_dir
        self.name: str = name

        self.dir: str = parent_dir + "/stat_" + self.name
        self.date: datetime = datetime.now()
        self.bal_start: int = 0
        self.bal_end: int = 0
        self.ope_list: List[Operation] = []
        self.ope_sum: float = 0.0
        self.file_sync: bool = True

        self.logger.debug("parent_dir = %s", self.parent_dir)
        self.logger.debug("name = %s", self.name)
        self.logger.debug("dir = %s", self.dir)

        self.logger.debug("Read dir")
        self.read_dir()

    def __str__(self) -> str:

        return (f"{self.name}, {self.date.strftime(FMT_DATE)}, {self.bal_start}, {self.bal_end},"
                f"{self.ope_sum}")

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
        ret += f"{indent_str}operations sum : {str(self.ope_sum)}\n"
        ret += f"{indent_str}balance diff : {str(self.ope_sum - self.bal_end)}\n"
        ret += f"{indent_str}operations : [\n"
        for operation in self.ope_list:
            ret += f"{indent_str}    {{\n"
            ret += operation.get_str(indent + 2) + "\n"
            ret += f"{indent_str}    }}\n"
        ret += f"{indent_str}]"

        return ret

    def get_closest_ope(self, ope_list: List[Operation]) -> Operation:
        """
        Get closest operation from list
        None if not found
        """

        # Operation to return
        ope_ret: Operation = ope_list[0]

        # While operation in list
        while (ope_ret in ope_list) and (ope_ret is not None):

            # Get operation index in statement
            ope_ret_idx = self.ope_list.index(ope_ret)

            # If first operation in list is first operation in statement
            if self.ope_list.index(ope_list[0]) == 0:
                # Search forward
                ope_ret_idx = ope_ret_idx + 1
            # Else, first operation in list is not first one
            else:
                # Search backward
                ope_ret_idx = ope_ret_idx - 1

            # If operation out of statement
            if ope_ret_idx < 0 or ope_ret_idx >= len(self.ope_list):
                ope_ret = None
            else:
                ope_ret = self.ope_list[ope_ret_idx]

        return ope_ret

    def set_name(self, name: str) -> None:
        """
        Set name
        Update dir accordingly

        Args:
            name (str): Name
        """

        self.name = name
        self.dir: str = self.parent_dir + "/stat_" + self.name

    def _read_info(self) -> None:

        file_name: str = self.dir + "/info.json"

        if not os.path.exists(file_name):
            self.logger.debug("File %s does not exist", file_name)
            return

        self.logger.debug("Open %s for reading", file_name)
        with open(file_name, "r", encoding="utf8") as file:

            data = json.load(file)

            if "name" in data:
                self.name = data["name"]
                self.logger.info("name = %s", self.name)
            if "date" in data:
                self.date = datetime.strptime(data["date"], FMT_DATE)
                self.logger.info("date = %s", self.date.strftime(FMT_DATE))
            if "bal_start" in data:
                self.bal_start = data["bal_start"]
                self.logger.info("bal_start = %s", self.bal_start)
            if "bal_end" in data:
                self.bal_end = data["bal_end"]
                self.logger.info("bal_end = %s", self.bal_end)

    def _read_ope_list(self) -> None:

        file_name: str = self.dir + "/ope_list.csv"

        if not os.path.exists(file_name):
            self.logger.debug("File %s does not exist", file_name)
            return

        self.logger.debug("Open %s for reading", file_name)
        with open(file_name, "r", encoding="utf8") as file:

            reader = csv.DictReader(file)

            self.ope_list.clear()
            self.ope_sum = 0.0

            for row in reader:

                self.logger.debug("Init operation")
                ope = Operation(datetime.strptime(row["date"], FMT_DATE), row["mode"],
                                row["tier"], row["cat"], row["desc"], float(row["amount"]))
                self.logger.debug("Operation inited : %s", ope)

                self.ope_list.append(ope)
                self.ope_sum += + ope.amount

            self.file_sync = True

    def read_dir(self) -> None:
        """
        Read from folder
        """

        if not os.path.isdir(self.dir):
            self.logger.debug("Folder %s does not exist", self.dir)
            return

        self.logger.debug("Read info")
        self._read_info()

        self.ope_list.clear()
        self.logger.debug("Read operations list")
        self._read_ope_list()

        self.logger.debug("File sync")
        self.file_sync = True

    def _write_info(self) -> None:

        file_name: str = self.dir + "/info.json"
        self.logger.debug("Open %s for writing", file_name)
        with open(file_name, "w", encoding="utf8") as file:

            data = {
                "name" : self.name,
                "date" : self.date.strftime(FMT_DATE),
                "bal_start" : self.bal_start,
                "bal_end" : self.bal_end,
            }

            self.logger.debug("Dump JSON to %s", file_name)
            json.dump(data, file)

    def _write_ope_list(self) -> None:

        file_name: str = self.dir + "/ope_list.csv"
        self.logger.debug("Open %s for writing", file_name)
        with open(file_name, "w", encoding="utf8") as file:

            writer = csv.DictWriter(file, Operation.CSV_KEY_LIST, delimiter=',', quotechar='"')

            self.logger.debug("Write header to %s", file_name)
            writer.writeheader()

            for ope in self.ope_list:

                row = {
                    "date": ope.date.strftime(FMT_DATE),
                    "mode": ope.mode,
                    "tier": ope.tier,
                    "cat": ope.cat,
                    "desc": ope.desc,
                    "amount": ope.amount,
                }

                self.logger.debug("Write row to %s", file_name)
                writer.writerow(row)

    def write_dir(self) -> None:
        """
        Write to folder
        """

        if not os.path.isdir(self.dir):
            self.logger.debug("Create folder %s", self.dir)
            os.mkdir(self.dir)

        self.logger.debug("Write info")
        self._write_info()

        self.logger.debug("Write operations list")
        self._write_ope_list()

        self.logger.debug("File sync")
        self.file_sync = True

    def add_ope(self, ope: Operation) -> None:
        """
        Add operation
        """

        idx = 0
        while idx < len(self.ope_list) and ope.date > self.ope_list[idx].date:
            idx = idx + 1

        self.ope_list.insert(idx, ope)
        self.ope_sum += ope.amount

        self.file_sync = False

    def add_ope_list(self, ope_list: List[Operation]) -> None:
        """
        Add operation list
        """

        for ope in ope_list:
            self.add_ope(ope)

    def remove_ope(self, ope: Operation) -> None:
        """
        Remove operation
        """

        if ope not in self.ope_list:
            return

        self.ope_list.remove(ope)
        self.ope_sum -= ope.amount

        self.file_sync = False

    def remove_ope_list(self, ope_list: List[Operation]) -> None:
        """
        Remove operation list
        """

        for ope in ope_list:
            self.remove_ope(ope)
