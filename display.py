"""
Display
"""

import curses
from curses import *
from datetime import datetime
from enum import IntEnum
import sys
import time
from typing import (TYPE_CHECKING, List, Tuple)

from utils import (OK, ERROR,
                   LEN_DATE, LEN_NAME, LEN_MODE, LEN_TIER, LEN_CAT, LEN_DESC, LEN_AMOUNT,
                   FMT_DATE)
from account import Account
from statement import Statement
from operation import Operation

if TYPE_CHECKING:
    from _curses import _CursesWindow
    Window = _CursesWindow
else:
    from typing import Any
    Window = Any

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
    SUB = 1
    INFO = 2
    INPUT = 3
    # CMD = 4
    # STATUS = 5
    LAST = INPUT

class DisplayCurses():
    """
    Display
    """

    def __init__(self, account: Account) -> None:

        # Account
        self.account: Account = account

        # Windows list
        self.win_list: List[Window] = [None] * (WinId.LAST + 1)

    def wrap(self, win_main: Window) -> None:
        """
        Curses wrapper
        """

        # Main window
        win_main_h = curses.LINES
        win_main_w = curses.COLS - 2

        # Sub main window
        win_sub_h = win_main_h - 2 - 2
        win_sub_w = int(2 * win_main_w / 3) - 2
        win_sub_y = 2
        win_sub_x = 2

        # win_cmd_h = 3
        # win_cmd_w = win_sub_w
        # win_cmd_y = win_main_h - win_cmd_h - 1
        # win_cmd_x = win_sub_x

        # win_status_h = 3
        # win_status_w = int(win_main_w / 3) - 2
        # win_status_y = win_main_h - win_status_h - 1
        # win_status_x = win_info_x

        # Info window
        win_info_h = int(win_sub_h / 2) - 1
        win_info_w = int(win_main_w / 3) - 2
        win_info_y = 2
        win_info_x = win_main_w - win_info_w - 1

        # Input window
        win_input_h = win_info_h
        win_input_w = win_info_w
        win_input_y = win_info_y + win_info_h + 1
        win_input_x = win_info_x

        curses.init_pair(ColorPairId.RED_BLACK, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(ColorPairId.GREEN_BLACK, curses.COLOR_GREEN, curses.COLOR_BLACK)

        self.win_list[WinId.MAIN] = win_main

        win_sub = curses.newwin(win_sub_h, win_sub_w, win_sub_y, win_sub_x)
        self.win_list[WinId.SUB] = win_sub

        win_info = curses.newwin(win_info_h, win_info_w, win_info_y, win_info_x)
        self.win_list[WinId.INFO] = win_info

        win_input = curses.newwin(win_input_h, win_input_w, win_input_y, win_input_x)
        win_input.keypad(True)
        self.win_list[WinId.INPUT] = win_input

        # win_cmd = curses.newwin(win_cmd_h, win_cmd_w, win_cmd_y, win_cmd_x)
        # self.win_list[WinId.CMD] = win_cmd

        # win_status = curses.newwin(win_status_h, win_status_w, win_status_y, win_status_x)
        # self.win_list[WinId.STATUS] = win_status

        self.account.disp_mgr.browse(self.win_list)

if __name__ == "__main__":

    ACCOUNT = Account()

    # Curses
    DISPLAY = DisplayCurses(ACCOUNT)
    wrapper(DISPLAY.wrap)

    sys.exit(0)
