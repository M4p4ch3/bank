
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

    # Window ID
    WIN_ID_MAIN = 0
    WIN_ID_INFO = 1
    WIN_ID_INPUT = 2
    WIN_ID_CMD = 3
    WIN_ID_STATUS = 4
    WIN_ID_LAST = WIN_ID_STATUS

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

        # Main window height
        self.win_main_h = curses.LINES
        win_main_w = curses.COLS - 2

        win_cmd_h = 3
        win_cmd_w = int(2 * win_main_w / 3) - 2
        win_cmd_y = self.win_main_h - win_cmd_h - 1
        win_cmd_x = 2

        win_info_h = int((self.win_main_h - win_cmd_h) / 2) - 2
        win_info_w = int(win_main_w / 3) - 2
        win_info_y = 2
        win_info_x = win_main_w - win_info_w - 1

        win_input_h = win_info_h
        win_input_w = win_info_w
        win_input_y = win_info_y + win_info_h + 1
        win_input_x = win_info_x

        win_status_h = win_cmd_h
        win_status_w = win_info_w
        win_status_y = win_cmd_y
        win_status_x = win_info_x

        curses.init_pair(self.COLOR_PAIR_ID_RED_BLACK, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(self.COLOR_PAIR_ID_GREEN_BLACK, curses.COLOR_GREEN, curses.COLOR_BLACK)

        self.win_list[self.WIN_ID_MAIN] = win_main

        win_info = curses.newwin(win_info_h, win_info_w, win_info_y, win_info_x)
        self.win_list[self.WIN_ID_INFO] = win_info

        win_input = curses.newwin(win_input_h, win_input_w, win_input_y, win_input_x)
        win_input.keypad(True)
        self.win_list[self.WIN_ID_INPUT] = win_input

        win_cmd = curses.newwin(win_cmd_h, win_cmd_w, win_cmd_y, win_cmd_x)
        self.win_list[self.WIN_ID_CMD] = win_cmd

        win_status = curses.newwin(win_status_h, win_status_w, win_status_y, win_status_x)
        self.win_list[self.WIN_ID_STATUS] = win_status

        self.ACCOUNT_browse()

    def ACCOUNT_disp(self, stat_first_idx: int, stat_hl: Statement) -> None:

        # Number of statements to display
        stat_disp_nb: int = self.win_main_h - 11
        if len(self.account.stat_list) < stat_disp_nb:
            stat_disp_nb = len(self.account.stat_list)
        # TODO
        # stat_last_idx

        # Use main window
        win: Window = self.win_list[self.WIN_ID_MAIN]

        win.clear()
        win.border()
        win.move(0, 2)
        win.addstr(" STATEMENTS ", A_BOLD)

        (y, x) = (2, 2)
        win.addstr(y, x, f"{self.SEP_STAT}")
        y = y + 1

        win.addstr(y, x, f"| ")
        win.addstr("name".ljust(LEN_NAME), A_BOLD)
        win.addstr(" | ")
        win.addstr("date".ljust(LEN_DATE), A_BOLD)
        win.addstr(" | ")
        win.addstr("start".ljust(LEN_AMOUNT), A_BOLD)
        win.addstr(" | ")
        win.addstr("end".ljust(LEN_AMOUNT), A_BOLD)
        win.addstr(" | ")
        win.addstr("diff".ljust(LEN_AMOUNT), A_BOLD)
        win.addstr(" | ")
        win.addstr("err".ljust(LEN_AMOUNT), A_BOLD)
        win.addstr(" |")
        y = y + 1

        # Statement separator or missing
        if stat_first_idx == 0:
            win.addstr(y, x, self.SEP_STAT)
        else:
            win.addstr(y, x, self.MISS_STAT)
        y = y + 1

        # For each statement in display range
        # TODO
        # for stat_idx in range(stat_first_idx, stat_last_idx):
        stat_idx = stat_first_idx
        while stat_idx < len(self.account.stat_list) and stat_idx < stat_first_idx + stat_disp_nb:

            stat: Statement = self.account.stat_list[stat_idx]

            disp_flag = A_NORMAL
            if stat == stat_hl:
                disp_flag += A_STANDOUT

            win.addstr(y, x, "| ")
            win.addstr(stat.name.ljust(LEN_NAME), disp_flag)
            win.addstr(" | ")
            win.addstr(stat.date.strftime(FMT_DATE).ljust(LEN_DATE), disp_flag)
            win.addstr(" | ")
            win.addstr(str(stat.bal_start).ljust(LEN_AMOUNT), disp_flag)
            win.addstr(" | ")
            win.addstr(str(stat.bal_end).ljust(LEN_AMOUNT), disp_flag)
            win.addstr(" | ")
            bal_diff = round(stat.bal_end - stat.bal_start, 2)
            if bal_diff >= 0.0:
                win.addstr(str(bal_diff).ljust(LEN_AMOUNT),
                           curses.color_pair(self.COLOR_PAIR_ID_GREEN_BLACK))
            else:
                win.addstr(str(bal_diff).ljust(LEN_AMOUNT),
                           curses.color_pair(self.COLOR_PAIR_ID_RED_BLACK))
            win.addstr(" | ")
            bal_err = round(stat.bal_start + stat.op_sum - stat.bal_end, 2)
            if bal_err == 0.0:
                win.addstr(str(bal_err).ljust(LEN_AMOUNT),
                           curses.color_pair(self.COLOR_PAIR_ID_GREEN_BLACK))
            else:
                win.addstr(str(bal_err).ljust(LEN_AMOUNT),
                           curses.color_pair(self.COLOR_PAIR_ID_RED_BLACK))
            win.addstr(" |")
            y = y + 1

            stat_idx = stat_idx + 1

        # Statement separator or missing
        if stat_idx == len(self.account.stat_list):
            win.addstr(y, x, self.SEP_STAT)
        else:
            win.addstr(y, x, self.MISS_STAT)
        y = y + 1

        # Slider
        # Move to top right of table
        (y, x) = (5, win.getyx()[1])
        for _ in range(int(stat_first_idx * stat_disp_nb / len(self.account.stat_list))):
            win.addstr(y, x, " ")
            y = y + 1
        for _ in range(int(stat_disp_nb * stat_disp_nb / len(self.account.stat_list)) + 1):
            win.addstr(y, x, " ", A_STANDOUT)
            y = y + 1

        win.refresh()

    def ACCOUNT_browse(self) -> None:

        # Index of first displayed statement
        stat_first_idx: int = 0

        # Highlighted statement
        stat_hl: Statement = None
        if len(self.account.stat_list) != 0:
            stat_hl = self.account.stat_list[0]

        while True:

            self.ACCOUNT_disp(stat_first_idx, stat_hl)

            # Status window
            win: Window = self.win_list[self.WIN_ID_STATUS]
            win.clear()
            win.border()
            win.addstr(0, 2, " STATUS ", A_BOLD)
            if self.account.is_unsaved:
                win.addstr(1, 2, "Unsaved", curses.color_pair(self.COLOR_PAIR_ID_RED_BLACK))
            else:
                win.addstr(1, 2, "Saved", curses.color_pair(self.COLOR_PAIR_ID_GREEN_BLACK))
            win.refresh()

            # Command window
            win: Window = self.win_list[self.WIN_ID_CMD]
            win.clear()
            win.border()
            win.addstr(0, 2, " COMMANDS ", A_BOLD)
            cmd_str = "Add : INS/+, Del : DEL/-"
            cmd_str = cmd_str + ", Open : ENTER"
            cmd_str = cmd_str + ", Save : S, Ret : ESCAPE"
            win.addstr(1, 2, cmd_str)
            win.refresh()

            key = self.win_list[self.WIN_ID_MAIN].getkey()

            # Highlight previous statement
            if key == "KEY_UP":

                # Highlight previous statement
                stat_hl_idx = self.account.stat_list.index(stat_hl) - 1
                if stat_hl_idx < 0:
                    stat_hl_idx = 0
                stat_hl = self.account.stat_list[stat_hl_idx]

                # If out of display range
                if stat_hl_idx < stat_first_idx:
                    # Previous page
                    stat_first_idx = stat_first_idx - 1
                    if stat_first_idx < 0:
                        stat_first_idx = 0

            # Highlight next statement
            if key == "KEY_DOWN":

                # Highlight next statement
                stat_hl_idx = self.account.stat_list.index(stat_hl) + 1
                if stat_hl_idx >= len(self.account.stat_list):
                    stat_hl_idx = len(self.account.stat_list) - 1
                stat_hl = self.account.stat_list[stat_hl_idx]

                # If out of display range
                if stat_hl_idx - stat_first_idx >= self.win_main_h - 11:
                    # Next page
                    stat_first_idx = stat_first_idx + 1
                    if stat_first_idx > len(self.account.stat_list) - (self.win_main_h - 11):
                        stat_first_idx = len(self.account.stat_list) - (self.win_main_h - 11)

            # Previous page
            elif key == "KEY_PPAGE":

                # Previous page
                stat_first_idx = stat_first_idx - 3
                if stat_first_idx < 0:
                    stat_first_idx = 0

                # If out of display range
                stat_hl_idx = self.account.stat_list.index(stat_hl)
                if stat_hl_idx < stat_first_idx:
                    stat_hl = self.account.stat_list[stat_first_idx]
                elif stat_hl_idx >= stat_first_idx + self.win_main_h - 11:
                    stat_hl = self.account.stat_list[stat_first_idx + self.win_main_h - 11 - 1]

            # Next page
            elif key == "KEY_NPAGE":

                # Next page
                stat_first_idx = stat_first_idx + 3
                if stat_first_idx > len(self.account.stat_list) - (self.win_main_h - 11):
                    stat_first_idx = len(self.account.stat_list) - (self.win_main_h - 11)
                    if stat_first_idx < 0:
                        stat_first_idx = 0

                # If out of display range
                stat_hl_idx = self.account.stat_list.index(stat_hl)
                if stat_hl_idx < stat_first_idx:
                    stat_hl = self.account.stat_list[stat_first_idx]
                elif stat_hl_idx >= stat_first_idx + self.win_main_h - 11:
                    stat_hl = self.account.stat_list[stat_first_idx + self.win_main_h - 11 - 1]

            # Add statement
            elif key in ("KEY_IC", "+"):
                self.ACCOUNT_addStat()

            # Delete highlighted statement
            elif key in ("KEY_DC", "-"):
                self.ACCOUNT_del_stat(stat_hl)
                # Reset highlighted statement
                stat_hl = self.account.stat_list[0]

            # Open highligthed statement
            elif key == "\n":
                stat_hl.disp_mgr.browse(self.win_list[self.WIN_ID_MAIN])

            elif key == "s":
                self.account.save()
                pass

            elif key == '\x1b':
                if self.account.is_unsaved:
                    # Input window
                    win: Window = self.win_list[self.WIN_ID_INPUT]
                    win.clear()
                    win.border()
                    win.addstr(0, 2, " UNSAVED CHANGES ", A_BOLD)
                    win.addstr(2, 2, "Save ? (y/n) : ")
                    save_c = win.getch()
                    if save_c != ord('n'):
                        win.addstr(4, 2, f"Saving")
                        win.refresh()
                        time.sleep(1)
                        self.account.save()
                    else:
                        win.addstr(4, 2, f"Discard changes",
                                   curses.color_pair(self.COLOR_PAIR_ID_RED_BLACK))
                        win.refresh()
                        time.sleep(1)
                break

    def ACCOUNT_addStat(self) -> None:

        # Use input window
        win: Window = self.win_list[self.WIN_ID_INPUT]

        win.clear()
        win.border()
        win.move(0, 2)
        win.addstr(" STATEMENT ", A_BOLD)

        (y, x) = (2, 2)
        win.addstr(y, x, "date : ")
        y = y + 1
        win.addstr(y, x, "start balance : ")
        y = y + 1
        win.addstr(y, x, "end balance   : ")
        y = y + 1

        win.keypad(False)
        curses.echo()

        (y, x) = (2, 2)

        is_converted = False
        while not is_converted:
            win.addstr(y, x, "date :                  ")
            win.addstr(y, x, "date : ")
            val_str = win.getstr().decode(encoding="utf-8")
            try:
                date = datetime.strptime(val_str, FMT_DATE)
                is_converted = True
            except ValueError:
                pass

        y = y + 1

        is_converted = False
        while not is_converted:
            win.addstr(y, x, "start balance :         ")
            win.addstr(y, x, "start balance : ")
            val_str = win.getstr().decode(encoding="utf-8")
            try:
                bal_start = float(val_str)
                is_converted = True
            except ValueError:
                pass

        y = y + 1

        is_converted = False
        while not is_converted:
            win.addstr(y, x, "end balance :           ")
            win.addstr(y, x, "end balance : ")
            val_str = win.getstr().decode(encoding="utf-8")
            try:
                bal_end = float(val_str)
                is_converted = True
            except ValueError:
                pass

        y = y + 1

        win.keypad(True)
        curses.noecho()

        # Statement CSV file does not exit
        # Read will create it
        stat = Statement(date.strftime(FMT_DATE), bal_start, bal_end, self.account)
        stat.read()

        # Append statement to statements list
        self.account.insertStat(stat)

    def ACCOUNT_del_stat(self, stat: Statement) -> None:

        # Input window
        win: Window = self.win_list[self.WIN_ID_INPUT]
        win.clear()
        win.border()
        win.addstr(0, 2, " DELETE STATEMENT ", A_BOLD)
        win.addstr(2, 2, "Confirm ? (y/n) : ")
        confirm_c = win.getch()
        if confirm_c != ord('y'):
            win.addstr(7, 2, f"Canceled", curses.color_pair(self.COLOR_PAIR_ID_RED_BLACK))
            win.refresh()
            time.sleep(1)
            return

        # Delete highlighted statement
        self.account.del_stat(stat)

if __name__ == "__main__":

    ACCOUNT = Account()

    # Curses
    DISPLAY = DisplayCurses(ACCOUNT)
    wrapper(DISPLAY.main)

    sys.exit(0)
