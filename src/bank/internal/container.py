"""
bank/internal/container
"""

import csv
import logging
from typing import (List, Tuple)

from bank.internal.item import Item
from bank.utils.error import NoOverrideError
from bank.utils.return_code import RetCode

class Container():
    """
    Container
    """

    def __init__(self, name: str, dir_path: str, item_list_name: str) -> None:

        self.logger = logging.getLogger("Container")
        self.name = name
        self.dir_path = dir_path
        self.file_path = dir_path + "/" + name + ".csv"
        self.item_list_name = item_list_name
        self.item_list: List[Item] = []
        self.is_saved: bool = True

    def raise_no_override(self, method: str = "") -> None:
        """
        Raise method not overriden exception

        Args:
            method_name (str, optional): Method name. Defaults to "".
        """

        raise NoOverrideError(
            base_class="Container",
            derived_class=type(self).__name__,
            method=method)

    def to_string(self, indent: int = 0) -> str:
        """
        To string

        Args:
            indent (int): Indentation level

        Returns:
            str: String
        """

        indent_str = ""
        for _ in range(indent):
            indent_str += "    "

        ret = ""
        ret += f"{indent_str}name : {self.name}\n"
        ret += f"{indent_str}file path : {self.file_path}\n"
        ret += f"{indent_str}{self.item_list_name} : [\n"
        for item in self.item_list:
            ret += item.to_string(indent=(indent + 1))
        ret += f"{indent_str}]\n"

        return ret

    def init_item(self) -> Item:
        """
        Init item
        """
        self.raise_no_override("init_item")
        return Item()

    def add_item(self, item: Item) -> None:
        """
        Add item to list

        Args:
            item (Item): Item
        """

        # Find index
        idx = 0
        while idx < len(self.item_list) and item.key > self.item_list[idx].key:
            idx = idx + 1

        # Insert item at dedicated index
        self.item_list.insert(idx, item)

        self.is_saved = False

    def remove_item(self, item: Item) -> None:
        """
        Remove item from list

        Args:
            item (Item): Item
        """

        if item not in self.item_list:
            return

        self.item_list.remove(item)
        self.is_saved = False

    def reset(self) -> None:
        """
        Reset
        """

        self.item_list.clear()
        self.is_saved = False

    def import_file(self) -> RetCode:
        """
        Import file
        """

        try:
            # Open CSV file
            file = open(self.file_path, "r", encoding="utf8")
        except FileNotFoundError:
            self.logger.error("import_file : Open %s file FAILED", self.file_path)
            return RetCode.ERROR

        self.reset()

        reader = csv.DictReader(file)

        for row in reader:

            item = self.init_item()

            ret = item.update_from_csv(row)
            if ret != RetCode.OK:
                self.logger.error("import_file : Create item of %s FAILED", self.name)
                return ret

            self.add_item(item)

        file.close()

        return RetCode.OK

    def export_file(self):
        """
        Export file
        """

        try:
            # Open statements CSV file
            file = open(self.file_path, "w", encoding="utf8")
        except FileNotFoundError:
            self.logger.error("export_file : Open %s file FAILED", self.file_path)
            return

        file_csv = csv.writer(file, delimiter=',', quotechar='"')

        # For each statement
        for stat in self.item_list:

            # Create statement line
            stat_csv = [stat.date.strftime(FMT_DATE),
                        str(stat.bal_start), str(stat.bal_end)]

            # Write statement line to CSV file
            file_csv.writerow(stat_csv)

        self.is_saved = True

        file.close()
