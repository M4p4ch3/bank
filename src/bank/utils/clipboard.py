"""
Clipboard
"""

from typing import (List, Any)

class Clipboard():
    """
    Clipboard
    """

    def __init__(self) -> None:

        # Items list
        self.item_list: List[Any] = []

    def get_len(self) -> int:
        """
        Get items list length
        """

        return len(self.item_list)

    def clear(self) -> None:
        """
        Clean items list
        """

        if len(self.item_list) > 0:
            self.item_list.clear()

    def set(self, item_list: List[Any]) -> None:
        """
        Set items list

        Args:
            item_list (List[Any]): Items list to set in buffer
        """

        self.clear()

        for item in item_list:

            if hasattr(item, "copy"):
                # Deep copy
                item_new = item.copy()
            else:
                item_new = item

            self.item_list.append(item_new)

    def get(self) -> List[Any]:
        """
        Get items list

        Returns:
            List[Any]: Items list
        """

        item_list = []

        for item in self.item_list:

            if hasattr(item, "copy"):
                # Deep copy
                item_new = item.copy()
            else:
                item_new = item

            item_list.append(item_new)

        return item_list
