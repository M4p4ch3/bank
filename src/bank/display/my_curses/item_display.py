"""
display/curses/item
"""

import curses
from curses import (A_NORMAL, A_BOLD, A_STANDOUT)
from typing import (Any, Tuple)

from bank.display.my_curses.main import (WinId, DisplayerMain)

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

        (win_y, win_x) = (2, 2)

        for field_idx in range(self.field_nb):

            (name, value) = self.get_item_field(field_idx)

            disp_flag = A_NORMAL
            if field_idx == field_hl_idx:
                disp_flag += A_STANDOUT

            win.addstr(win_y, win_x, f"{name} : {value}", disp_flag)
            win_y += 1

        win_y += 1
        win.move(win_y, win_x)

        # win.refresh()

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

        (win_y, win_x) = win.getyx()

        # Field value edit prompt
        win.addstr(win_y, win_x, "Value : ")

        # Get field value input
        win.keypad(False)
        curses.echo()

        val_str = ""
        try:
            val_str = win.getstr().decode(encoding="utf-8")
        except UnicodeDecodeError:
            pass

        win.keypad(True)
        curses.noecho()

        # If field value input
        if val_str != "":

            # Set field value
            is_edited = self.set_item_field(field_idx, val_str)

        return is_edited

    def edit_item(self, force_iterate: bool = False) -> bool:
        """
        Edit item
        """

        is_edited: bool = False
        field_hl_idx: int = 0
        win = self.disp.win_list[WinId.RIGHT_BOT]

        win.clear()
        win.keypad(True)

        while True:

            self.display_item_win(win, field_hl_idx)
            (win_y, win_x) = win.getyx()

            win.clrtoeol()
            win.border()
            win.move(0, 2)
            win.addstr(f" {self.name} ", A_BOLD)

            win.move(win_y, win_x)

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
                    if field_hl_idx >= self.field_nb:
                        field_hl_idx = self.field_nb - 1

                # Edit highlighted field
                elif key == "\n":

                    is_edited_single = self.edit_item_field(win, field_hl_idx)
                    if is_edited_single:
                        is_edited = True

                # Exit
                elif key == '\x1b':
                    break

        win.clear()
        win.refresh()

        return is_edited
