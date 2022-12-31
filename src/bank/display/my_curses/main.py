"""
display/curses/main
"""

import curses
from curses import (A_NORMAL, A_BOLD, A_STANDOUT)
from enum import IntEnum
from typing import (Any, List)

from bank.utils.clipboard import Clipboard


class ColorPairId(IntEnum):
    """
    Curses color pair ID
    """

    RED_BLACK = 1
    GREEN_BLACK = 2

class WinId(IntEnum):
    """
    Window ID
    """

    MAIN = 0
    LEFT = 1
    RIGHT_TOP = 2
    RIGHT_BOT = 3
    LAST = RIGHT_BOT

class NoOverrideError(Exception):
    """
    Exception raised for not overriden method
    """

    def __init__(self, base_class: str = "", derived_class: str = "", method: str = "") -> None:
        msg = f"{base_class}.{method} not overriden in {derived_class}"
        super().__init__(msg)

class DisplayerMain():
    """
    Cruses main display
    """

    PADDING_Y = 0
    PADDING_X = 1
    BORDER_H = 1
    BORDER_W = BORDER_H

    def __init__(self, win_main: Any) -> None:

        # Windows list
        self.win_list: List[Any] = [None] * (WinId.LAST + 1)

        # Item list clipboard
        self.item_list_clipboard: Clipboard = Clipboard()

        # Last browsed container displayer
        self.cont_disp_last: Any = None

        # Main window
        (win_main_h, win_main_w) = win_main.getmaxyx()
        self.win_list[WinId.MAIN] = win_main
        win_main.keypad(True)

        # Left main window
        win_h = win_main_h - 2 * self.BORDER_H - 2 * self.PADDING_Y
        win_w = int(2 * win_main_w / 3) - 2 * self.BORDER_W
        win_y = self.BORDER_H + self.PADDING_Y
        win_x = self.BORDER_W + self.PADDING_X
        win = curses.newwin(win_h, win_w, win_y, win_x)
        self.win_list[WinId.LEFT] = win
        win_left_h = win_h

        # Top right window
        win_h = int(win_left_h / 2) - int(self.PADDING_Y / 2)
        win_w = int(win_main_w / 3) - 2 * self.BORDER_W - self.PADDING_X
        win_y = self.BORDER_H + self.PADDING_Y
        win_x = win_main_w - self.BORDER_W - win_w - self.PADDING_X
        win = curses.newwin(win_h, win_w, win_y, win_x)
        self.win_list[WinId.RIGHT_TOP] = win

        # Bottom right window
        win_h = int(win_left_h / 2) - int(self.PADDING_Y / 2)
        win_w = int(win_main_w / 3) - 2 * self.BORDER_W - self.PADDING_X
        win_y = win_main_h - self.BORDER_H - win_h - self.PADDING_Y
        win_x = win_main_w - self.BORDER_W - win_w - self.PADDING_X
        win = curses.newwin(win_h, win_w, win_y, win_x)
        self.win_list[WinId.RIGHT_BOT] = win

        curses.init_pair(ColorPairId.RED_BLACK, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(ColorPairId.GREEN_BLACK, curses.COLOR_GREEN, curses.COLOR_BLACK)

    def add_log(self, msg: str) -> None:
        """
        Add log message

        Args:
            msg (str): Log message
        """

        win = self.win_list[WinId.RIGHT_BOT]
        msg += "\n"
        win.addstr(msg)
        win.refresh()

    def clear_log(self) -> None:
        """
        Clear log
        """

        win = self.win_list[WinId.RIGHT_BOT]
        win.clear()

    def display_choice_menu(self, name: str, msg: str, choice_list: List[str]) -> int:
        """
        Display choice menu

        Args:
            choice_list (List[str]): Choice list

        Returns:
            int: Selected choice index
        """

        choice_hl_idx: int = 0

        # Bottom right window
        win = self.win_list[WinId.RIGHT_BOT]

        win.clear()
        win.border()
        win.addstr(0, 2, f" {name} ", A_BOLD)
        win.addstr(2, 2, msg)
        win.keypad(1)

        while True:

            (win_y, win_x) = (4, 2)

            for choice in choice_list:

                choice_idx = choice_list.index(choice)
                disp_flag = A_NORMAL
                if choice_idx == choice_hl_idx:
                    disp_flag += A_STANDOUT
                win.addstr(win_y, win_x, choice, disp_flag)
                win_y += 1

            # key = win.getkey()
            key = win.getch()
            win.addstr(0, 0, f"\"{key}\"")
            win.refresh()

            # Highlight previous field
            if key in ["KEY_UP", 259]:
                choice_hl_idx -= 1
                if choice_hl_idx < 0:
                    choice_hl_idx = 0

            # Highlight next field
            elif key in ["KEY_DOWN", 258]:
                choice_hl_idx += 1
                if choice_hl_idx >= len(choice_list):
                    choice_hl_idx = len(choice_list) - 1

            # Select highlighted choice
            elif key in [10]:
                break

            # Exit
            # esc, backspace
            elif key in [27, 8]:
                choice_hl_idx = -1
                break

        win.clear()
        win.refresh()

        return choice_hl_idx
