
"""
Display
"""

import curses
from curses import *
from datetime import datetime
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

class DisplayCurses():
    """
    Display
    """

    # Color pair ID
    COLOR_PAIR_ID_RED_BLACK = 1
    COLOR_PAIR_ID_GREEN_BLACK = 2

    # TODO Enum
    # from enum import Enum
    # class WinId(Enum):
    #     BACK = 0
    #     MAIN = 1
    #     INFO = 2

    # Window ID
    WIN_ID_MAIN = 0
    WIN_ID_SUB = 1
    WIN_ID_INFO = 2
    WIN_ID_INPUT = 3
    # WIN_ID_CMD = 4
    # WIN_ID_STATUS = 5
    WIN_ID_LAST = WIN_ID_INPUT

    # Statement separator
    SEP_STAT = "|"
    SEP_STAT += "-" + "-".ljust(LEN_NAME, "-") + "-|"
    SEP_STAT += "-" + "-".ljust(LEN_DATE, "-") + "-|"
    SEP_STAT += "-" + "-".ljust(LEN_AMOUNT, "-") + "-|"
    SEP_STAT += "-" + "-".ljust(LEN_AMOUNT, "-") + "-|"
    SEP_STAT += "-" + "-".ljust(LEN_AMOUNT, "-") + "-|"
    SEP_STAT += "-" + "-".ljust(LEN_AMOUNT, "-") + "-|"

    # # Statement header
    # HEADER_STAT = "|"
    # HEADER_STAT += " " + "name".ljust(LEN_NAME, " ") + " |"
    # HEADER_STAT += " " + "date".ljust(LEN_DATE, " ") + " |"
    # HEADER_STAT += " " + "start".ljust(LEN_AMOUNT, " ") + " |"
    # HEADER_STAT += " " + "end".ljust(LEN_AMOUNT, " ") + " |"
    # HEADER_STAT += " " + "diff".ljust(LEN_AMOUNT, " ") + " |"
    # HEADER_STAT += " " + "err".ljust(LEN_AMOUNT, " ") + " |"

    # Statement missing
    MISS_STAT = "|"
    MISS_STAT += " " + "...".ljust(LEN_NAME, " ") + " |"
    MISS_STAT += " " + "...".ljust(LEN_DATE, " ") + " |"
    MISS_STAT += " " + "...".ljust(LEN_AMOUNT, " ") + " |"
    MISS_STAT += " " + "...".ljust(LEN_AMOUNT, " ") + " |"
    MISS_STAT += " " + "...".ljust(LEN_AMOUNT, " ") + " |"

    # Operation separator
    SEP_OP = "|"
    SEP_OP += "-" + "-".ljust(LEN_DATE, "-") + "-|"
    SEP_OP += "-" + "-".ljust(LEN_MODE, "-") + "-|"
    SEP_OP += "-" + "-".ljust(LEN_TIER, "-") + "-|"
    SEP_OP += "-" + "-".ljust(LEN_CAT, "-") + "-|"
    SEP_OP += "-" + "-".ljust(LEN_DESC, "-") + "-|"
    SEP_OP += "-" + "-".ljust(LEN_AMOUNT, "-") + "-|"

    # # Operation header
    # HEADER_OP = "|"
    # HEADER_OP += " " + "date".ljust(LEN_DATE, " ") + " |"
    # HEADER_OP += " " + "mode".ljust(LEN_MODE, ' ') + " |"
    # HEADER_OP += " " + "tier".ljust(LEN_TIER, ' ') + " |"
    # HEADER_OP += " " + "category".ljust(LEN_CAT, ' ') + " |"
    # HEADER_OP += " " + "description".ljust(LEN_DESC, ' ') + " |"
    # HEADER_OP += " " + "amount".ljust(LEN_AMOUNT, ' ') + " |"

    # Operation missing
    MISS_OP = "|"
    MISS_OP += " " + "...".ljust(LEN_DATE, ' ') + " |"
    MISS_OP += " " + "...".ljust(LEN_MODE, ' ') + " |"
    MISS_OP += " " + "...".ljust(LEN_TIER, ' ') + " |"
    MISS_OP += " " + "...".ljust(LEN_CAT, ' ') + " |"
    MISS_OP += " " + "...".ljust(LEN_DESC, ' ') + " |"
    MISS_OP += " " + "...".ljust(LEN_AMOUNT, ' ') + " |"

    def __init__(self, account: Account) -> None:

        # Account
        self.account: Account = account

        # Main window height
        self.win_main_h: int = 0

        # TODO define and use
        # Highlighted item
        self.itemHl = None
        # Focused item (first item in view)
        self.itemFocus = None

        # Windows list
        self.win_list: List[Window] = [None] * (self.WIN_ID_LAST + 1)

    def main(self, win_main: Window) -> None:

        # Main window
        self.win_main_h = curses.LINES
        self.win_main_w = curses.COLS - 2

        # Sub main window
        win_sub_h = self.win_main_h - 2 - 2
        win_sub_w = int(2 * self.win_main_w / 3) - 2
        win_sub_y = 2
        win_sub_x = 2

        # win_cmd_h = 3
        # win_cmd_w = win_sub_w
        # win_cmd_y = self.win_main_h - win_cmd_h - 1
        # win_cmd_x = win_sub_x

        # win_status_h = 3
        # win_status_w = int(win_main_w / 3) - 2
        # win_status_y = self.win_main_h - win_status_h - 1
        # win_status_x = win_info_x

        # Info window
        win_info_h = int(win_sub_h / 2) - 1
        win_info_w = int(self.win_main_w / 3) - 2
        win_info_y = 2
        win_info_x = self.win_main_w - win_info_w - 1

        # Input window
        win_input_h = win_info_h
        win_input_w = win_info_w
        win_input_y = win_info_y + win_info_h + 1
        win_input_x = win_info_x

        curses.init_pair(self.COLOR_PAIR_ID_RED_BLACK, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(self.COLOR_PAIR_ID_GREEN_BLACK, curses.COLOR_GREEN, curses.COLOR_BLACK)

        self.win_list[self.WIN_ID_MAIN] = win_main

        win_sub = curses.newwin(win_sub_h, win_sub_w, win_sub_y, win_sub_x)
        self.win_list[self.WIN_ID_SUB] = win_sub

        win_info = curses.newwin(win_info_h, win_info_w, win_info_y, win_info_x)
        self.win_list[self.WIN_ID_INFO] = win_info

        win_input = curses.newwin(win_input_h, win_input_w, win_input_y, win_input_x)
        win_input.keypad(True)
        self.win_list[self.WIN_ID_INPUT] = win_input

        # win_cmd = curses.newwin(win_cmd_h, win_cmd_w, win_cmd_y, win_cmd_x)
        # self.win_list[self.WIN_ID_CMD] = win_cmd

        # win_status = curses.newwin(win_status_h, win_status_w, win_status_y, win_status_x)
        # self.win_list[self.WIN_ID_STATUS] = win_status

        self.account.disp_mgr.browse(self.win_list)

if __name__ == "__main__":

    ACCOUNT = Account()

    # Curses
    DISPLAY = DisplayCurses(ACCOUNT)
    wrapper(DISPLAY.main)

    sys.exit(0)
