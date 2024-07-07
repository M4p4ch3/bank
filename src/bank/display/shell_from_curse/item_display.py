"""
display/shell/item
"""

from typing import (Any, Tuple)

from bank.display.shell.main import (WinId, DisplayerMain)

class DisplayerItem():
    """
    Curses item display
    """

    SEPARATOR = ""
    HEADER = ""
    MISSING = ""

    def __init__(self, disp: DisplayerMain) -> None:

        # Main display
        self.disp = disp

        self.field_nb = 0

        self.name = ""

    def set_item(self, item: Any):
        """Set item"""
        _ = item

    def get_item_field(self, field_idx: int) -> Tuple[str, str]:
        """Get item field"""
        _ = field_idx
        return ("", "")

    def set_item_field(self, field_idx: int, val_str: str) -> bool:
        """Set item field"""
        _ = field_idx
        _ = val_str
        return False

    def display_item_win(self, win: Any, field_hl_idx: int = 0) -> None:
        """
        Display item in window
        """

        for field_idx in range(self.field_nb):

            (name, value) = self.get_item_field(field_idx)

            print(f"{name} : {value}")

    def edit_item_field(self, win: Any, field_idx: int) -> bool:
        """
        Edit item field
        Print prompt to edit item field

        Args:
            win (Window): Window to use
            field_idx (int): Index of field to edit

        Returns:
            bool: Is item field edited
        """

        is_edited: bool = False

        val_str = input("Value : ")
        if val_str != "":
            is_edited = self.set_item_field(field_idx, val_str)

        return is_edited

    def edit_item(self, force_iterate: bool = False) -> bool:
        """
        Edit item
        """

        is_edited: bool = False
        field_hl_idx: int = 0

        while True:

            self.display_item_win(win, field_hl_idx)

            print(f" {self.name} ")

            if force_iterate:

                self.edit_item_field(win, field_hl_idx)
                field_hl_idx += 1
                if field_hl_idx >= self.field_nb:
                    break

            else:

                # Get key
                key = win.getkey()

                # Highlight previous field
                if key == "KEY_UP":
                    field_hl_idx -= 1
                    if field_hl_idx < 0:
                        field_hl_idx = 0

                # Highlight next field
                elif key == "KEY_DOWN":
                    field_hl_idx += 1
                    if field_hl_idx > self.field_nb:
                        field_hl_idx = self.field_nb

                # Edit highlighted field
                elif key == "\n":

                    is_edited_single = self.edit_item_field(win, field_hl_idx)
                    if is_edited_single:
                        is_edited = True

                # Exit
                elif key == '\x1b':
                    break

        return is_edited
