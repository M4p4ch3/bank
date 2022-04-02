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

    # TODO update dir to parent_dir

    CSV_KEY_LIST = ["id", "name"]

    def __init__(self, parent_dir: str, name: str = "") -> None:

        self.logger = logging.getLogger("Account")

        self.parent_dir: str = parent_dir
        self.name: str = name

        self.dir: str = self.parent_dir + "/account_" + self.name
        self.stat_list: List[Statement] = []
        self.file_sync: bool = True

        self.logger.debug("parent_dir = %s", self.parent_dir)
        self.logger.debug("name = %s", self.name)
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

    def set_name(self, name: str) -> None:
        """
        Set name
        Update dir accordingly

        Args:
            name (str): Name
        """

        self.name = name
        self.dir: str = self.parent_dir + "/account_" + self.name

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
                stat_name = item[len("stat_"):]
                self.logger.debug("Found statement %s", stat_name)

                self.logger.debug("Init statement %s", stat_name)
                stat = Statement(self.dir, stat_name)
                self.logger.debug("Statement inited : %s", stat)

                self.stat_list.append(stat)

    def read_dir(self) -> None:
        """
        Read from folder
        """

        if not os.path.isdir(self.dir):
            self.logger.debug("Folder %s does not exist", self.dir)
            return

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
                stat_name = item[len("stat_"):]
                self.logger.debug("Found statement %s", stat_name)

                # Should stat dir be removed ?
                remove_stat_dir: bool = True

                for stat in self.stat_list:
                    if stat.name == stat_name:
                        # Stat still in list, dont remove
                        remove_stat_dir = False
                        break

                if remove_stat_dir:
                    # Stat dir not in list anymore, remove
                    self.logger.debug("Remove dir %s", item)
                    shutil.rmtree(self.dir + "/" + item)

        for stat in self.stat_list:
            self.logger.debug("Write statement %s to folder", stat.name)
            stat.write_dir()

    def write_dir(self) -> None:
        """
        Write to folder
        """

        if not os.path.isdir(self.dir):
            self.logger.debug("Create folder %s", self.dir)
            os.mkdir(self.dir)

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
