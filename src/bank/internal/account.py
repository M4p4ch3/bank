"""
Account
"""

from datetime import datetime
import json
import logging
import os
import shutil
from typing import List

from bank.internal.statement import Statement

class Account():
    """
    Account
    """

    CSV_KEY_LIST = ["id", "name"]

    def __init__(self, _dir: str) -> None:

        self.logger = logging.getLogger("Account")

        self.dir: str = _dir
        self.name: str = ""

        self.stat_list: List[Statement] = []

        self.file_sync: bool = True

        self.logger.debug("dir = %s", self.dir)

        self.logger.debug("Read dir")
        self.read_dir()

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

    def _read_info(self) -> None:

        file_name: str = self.dir + "/info.json"

        if not os.path.exists(file_name):
            self.logger.debug("File %s does not exist", file_name)
            return

        self.logger.debug("Open %s for reading", file_name)
        with open(file_name, "r") as file:

            data = json.load(file)

            if "name" in data:
                self.name = data["name"]
                self.logger.info("name = %s", self.name)

    def _read_stat_list(self) -> None:

        self.logger.debug("List dir %s", self.dir)
        for item in os.listdir(self.dir):
            if os.path.isdir(self.dir + "/" + item) and "stat_" in item:

                self.logger.debug("Create statement %s", item)
                stat = Statement(self.dir + "/" + item)
                self.logger.debug("Statement created : %s", stat)

                self.stat_list.append(stat)

    def read_dir(self) -> None:
        """
        Read from folder
        """

        if not os.path.isdir(self.dir):
            self.logger.debug("Create folder %s", self.dir)
            os.mkdir(self.dir)

        self.logger.debug("Read info")
        self._read_info()

        self.logger.debug("Read statements list")
        self._read_stat_list()

        self.logger.debug("File sync")
        self.file_sync = True

    def _write_info(self) -> None:

        file_name: str = self.dir + "/info.json"
        self.logger.debug("Open %s for writing", file_name)
        with open(file_name, "w") as file:

            data = {
                "name" : self.name,
            }

            self.logger.debug("Dump JSON to %s", file_name)
            json.dump(data, file)

    def _write_stat_list(self) -> None:

        self.logger.debug("List dir %s", self.dir)
        for item in os.listdir(self.dir):
            if os.path.isdir(self.dir + "/" + item) and "stat_" in item:

                self.logger.debug("Remove dir %s", item)
                shutil.rmtree(self.dir + "/" + item)

        for stat in self.stat_list:

            self.logger.debug("Create dir %s", self.dir + "/stat_" + stat.name)
            os.mkdir(self.dir + "/stat_" + stat.name)

            self.logger.debug("Write stat %s", stat.name)
            stat.write_dir()

    def write_dir(self) -> None:
        """
        Write to folder
        """

        self.logger.debug("Write info")
        self._write_info()

        self.logger.debug("Write statements list")
        self._write_stat_list()

        self.logger.debug("File sync")
        self.file_sync = True

    def add_stat(self, stat: Statement) -> None:
        """
        Add statement
        """

        idx = 0
        while idx < len(self.stat_list) and stat.date > self.stat_list[idx].date:
            idx = idx + 1

        self.stat_list.insert(idx, stat)

        self.file_sync = False

    def remove_stat(self, stat: Statement) -> None:
        """
        Remove statement
        """

        if stat not in self.stat_list:
            return

        self.stat_list.remove(stat)

        self.file_sync = False
