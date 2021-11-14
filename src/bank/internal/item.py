"""
bank/internal/item
"""

import logging
from typing import (List, Tuple)

from bank.utils.error import NoOverrideError
from bank.utils.return_code import RetCode

class Item():
    """
    Item
    """

    def __init__(self, key_list: List[str]) -> None:

        self.logger = logging.getLogger("Item")

        self.key_list = key_list

        self.dict = dict()

    def raise_no_override(self, method: str = "") -> None:
        """
        Raise method not overriden exception

        Args:
            method_name (str, optional): Method name. Defaults to "".
        """

        raise NoOverrideError(
            base_class="Item",
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

        self.raise_no_override("get_item_str")
        _ = indent
        return ""

    def get_field(self, field_idx: int) -> Tuple[str, str]:
        """
        Get field (key, value), identified by field index
        """

        if field_idx >= len(self.key_list):
            return ("", "")

        entry = self.dict[field_idx]
        key = entry[0]
        value = entry[1]

        return (key, value)

    def set_field

    def update_from_csv(self, row: dict) -> RetCode:
        """
        Update item from CSV row dict

        Args:
            row (dict): CSV row dict
        """

        self.raise_no_override("update_from_csv")
        _ = row
        return RetCode.ERROR
