
"""
Display
"""

import curses
from curses import *
from datetime import datetime
import sys
import time
from typing import (TYPE_CHECKING, List, Tuple)

from utils import (ERROR,
                   LEN_DATE, LEN_NAME, LEN_MODE, LEN_TIER, LEN_CAT, LEN_DESC, LEN_AMOUNT,
                   FMT_DATE)
from account import Account
from statement import Statement
from operation import (Operation, OperationCurses)

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
                self.STAT_browse(stat_hl)

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
        stat = Statement(date.strftime(FMT_DATE), bal_start, bal_end)
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

    def STAT_disp_op_list(self, stat: Statement,
        op_first_idx: int, op_hl: OperationCurses, op_listSel: List[OperationCurses]) -> None:

        op_disp_nb = self.win_main_h - 11
        if len(stat.op_list) < op_disp_nb:
            op_disp_nb = len(stat.op_list)

        # Use main window
        win: Window = self.win_list[self.WIN_ID_MAIN]

        win.clear()
        win.border()
        win.move(0, 2)
        win.addstr(" STATEMENT ", A_BOLD)

        (y, x) = (2, 2)
        win.addstr(y, x, self.SEP_OP)
        y = y + 1

        win.addstr(y, x, "| ")
        win.addnstr("date".ljust(LEN_DATE), LEN_DATE, A_BOLD)
        win.addstr(" | ")
        win.addnstr("mode".ljust(LEN_MODE), LEN_MODE, A_BOLD)
        win.addstr(" | ")
        win.addnstr("tier".ljust(LEN_TIER), LEN_TIER, A_BOLD)
        win.addstr(" | ")
        win.addnstr("cat".ljust(LEN_CAT), LEN_CAT, A_BOLD)
        win.addstr(" | ")
        win.addnstr("desc".ljust(LEN_DESC), LEN_DESC, A_BOLD)
        win.addstr(" | ")
        win.addnstr("amount".ljust(LEN_AMOUNT), LEN_AMOUNT, A_BOLD)
        win.addstr(" |")
        y = y + 1

        # Operation separator or missing
        if op_first_idx == 0:
            win.addstr(y, x, self.SEP_OP)
        else:
            win.addstr(y, x, self.MISS_OP)
        y = y + 1

        op_idx = op_first_idx
        while op_idx < len(stat.op_list) and op_idx < op_first_idx + op_disp_nb:

            op = stat.op_list[op_idx]

            disp_flag = A_NORMAL
            if op == op_hl:
                disp_flag += A_STANDOUT
            if op in op_listSel:
                disp_flag += A_BOLD

            win.addstr(y, x, "| ")
            win.addnstr(op.date.strftime(FMT_DATE).ljust(LEN_DATE), LEN_DATE, disp_flag)
            win.addstr(" | ")
            win.addnstr(op.mode.ljust(LEN_MODE), LEN_MODE, disp_flag)
            win.addstr(" | ")
            win.addnstr(op.tier.ljust(LEN_TIER), LEN_TIER, disp_flag)
            win.addstr(" | ")
            win.addnstr(op.cat.ljust(LEN_CAT), LEN_CAT, disp_flag)
            win.addstr(" | ")
            win.addnstr(op.desc.ljust(LEN_DESC), LEN_DESC, disp_flag)
            win.addstr(" | ")
            win.addnstr(str(op.amount).ljust(LEN_AMOUNT), LEN_AMOUNT, disp_flag)
            win.addstr(" |")
            y = y + 1

            op_idx = op_idx + 1

        # Operation separator or missing
        if op_idx == len(stat.op_list):
            win.addstr(y, x, self.SEP_OP)
        else:
            win.addstr(y, x, self.MISS_OP)
        y = y + 1

        if len(stat.op_list) != 0:
            # Slider
            # Move to top right of table
            (y, x) = (5, win.getyx()[1])
            for _ in range(int(op_first_idx * op_disp_nb / len(stat.op_list))):
                win.addstr(y, x, " ")
                y = y + 1
            for _ in range(int(op_disp_nb * op_disp_nb / len(stat.op_list))):
                win.addstr(y, x, " ", A_STANDOUT)
                y = y + 1

        win.refresh()

    def STAT_dispFields(self, stat: Statement) -> None:

        # Use info window
        win: Window = self.win_list[self.WIN_ID_INFO]

        win.clear()
        win.border()
        win.move(0, 2)
        win.addstr(" INFO ", A_BOLD)

        (y, x) = (2, 2)
        win.addstr(y, x, f"name : {stat.name}")
        y = y + 1
        win.addstr(y, x, f"date : {stat.date.strftime(FMT_DATE)}")
        y = y + 1
        win.addstr(y, x, f"start : {stat.bal_start}")
        y = y + 1
        win.addstr(y, x, f"end : {stat.bal_end}")
        y = y + 1
        win.addstr(y, x, f"actual end : {(stat.bal_start + stat.op_sum):.2f}")
        y = y + 1
        bal_diff = round(stat.bal_end - stat.bal_start, 2)
        win.addstr(y, x, f"diff : ")
        if bal_diff >= 0.0:
            win.addstr(str(bal_diff), curses.color_pair(self.COLOR_PAIR_ID_GREEN_BLACK))
        else:
            win.addstr(str(bal_diff), curses.color_pair(self.COLOR_PAIR_ID_RED_BLACK))
        y = y + 1
        bal_err = round(stat.bal_start + stat.op_sum - stat.bal_end, 2)
        win.addstr(y, x, f"err : ")
        if bal_err == 0.0:
            win.addstr(str(bal_err), curses.color_pair(self.COLOR_PAIR_ID_GREEN_BLACK))
        else:
            win.addstr(str(bal_err), curses.color_pair(self.COLOR_PAIR_ID_RED_BLACK))
        y = y + 1

        win.refresh()

    def STAT_browse(self, stat: Statement) -> None:

        # Selected operations list
        op_listSel: List[OperationCurses] = []

        # First displayed operation
        op_first_idx: int = 0

        # Highlighted operation
        op_hl: OperationCurses = None
        if len(stat.op_list) != 0:
            op_hl = stat.op_list[0]

        while True:

            self.STAT_disp_op_list(stat, op_first_idx, op_hl, op_listSel)
            self.STAT_dispFields(stat)

            # Command window
            win: Window = self.win_list[self.WIN_ID_CMD]
            win.clear()
            win.border()
            win.addstr(0, 2, " COMMANDS ", A_BOLD)
            cmd_str = "Add : INS/+, Del : DEL/-"
            cmd_str = cmd_str + ", Dupl : D, (Un)sel : SPACE, Move : M "
            cmd_str = cmd_str + ", Open : ENTER"
            cmd_str = cmd_str + ", Save : S, Ret : ESCAPE"
            win.addstr(1, 2, cmd_str)
            win.refresh()

            # Status window
            win: Window = self.win_list[self.WIN_ID_STATUS]
            win.clear()
            win.border()
            win.addstr(0, 2, " STATUS ", A_BOLD)
            if stat.is_unsaved:
                win.addstr(1, 2, "Unsaved", curses.color_pair(self.COLOR_PAIR_ID_RED_BLACK))
            else:
                win.addstr(1, 2, "Saved", curses.color_pair(self.COLOR_PAIR_ID_GREEN_BLACK))
            win.refresh()

            key = self.win_list[self.WIN_ID_MAIN].getkey()

            # Highlight previous operation
            if key == "KEY_UP":

                op_hl_idx = stat.op_list.index(op_hl) - 1
                if op_hl_idx < 0:
                    op_hl_idx = 0
                op_hl = stat.op_list[op_hl_idx]

                # If out of display range
                if op_hl_idx < op_first_idx:
                    # Previous page
                    op_first_idx = op_first_idx - 1
                    if op_first_idx < 0:
                        op_first_idx = 0

            # Highlight next operation
            elif key == "KEY_DOWN":

                op_hl_idx = stat.op_list.index(op_hl) + 1
                if op_hl_idx >= len(stat.op_list):
                    op_hl_idx = len(stat.op_list) - 1
                op_hl = stat.op_list[op_hl_idx]

                # If out of display range
                if op_hl_idx - op_first_idx >= self.win_main_h - 11:
                    # Next page
                    op_first_idx = op_first_idx + 1
                    if op_first_idx > len(stat.op_list) - (self.win_main_h - 11):
                        op_first_idx = len(stat.op_list) - (self.win_main_h - 11)

            # Previous page
            elif key == "KEY_PPAGE":

                # Previous page
                op_first_idx = op_first_idx - 3
                if op_first_idx < 0:
                    op_first_idx = 0

                # If out of display range
                op_hl_idx = stat.op_list.index(op_hl)
                if op_hl_idx < op_first_idx:
                    op_hl = stat.op_list[op_first_idx]
                elif op_hl_idx >= op_first_idx + self.win_main_h - 11:
                    op_hl = stat.op_list[op_first_idx + self.win_main_h - 11 - 1]

            # Next page
            elif key == "KEY_NPAGE":

                # Next page
                op_first_idx = op_first_idx + 3
                if op_first_idx > len(stat.op_list) - (self.win_main_h - 11):
                    op_first_idx = len(stat.op_list) - (self.win_main_h - 11)
                    if op_first_idx < 0:
                        op_first_idx = 0

                # If out of display range
                op_hl_idx = stat.op_list.index(op_hl)
                if op_hl_idx < op_first_idx:
                    op_hl = stat.op_list[op_first_idx]
                elif op_hl_idx >= op_first_idx + self.win_main_h - 11:
                    op_hl = stat.op_list[op_first_idx + self.win_main_h - 11 - 1]

            # (Un)select operation
            elif key == " ":
                # If operation not selected
                if op_hl not in op_listSel:
                    # Add operation to selected ones
                    op_listSel.append(op_hl)
                # Else, operation selected
                else:
                    # Remove operation from selected ones
                    op_listSel.remove(op_hl)

            # Add operation
            elif key in ("KEY_IC", "+"):
                self.STAT_addOp(stat)

            # Delete operation(s)
            elif key in ("KEY_DC", "-"):

                # If no selected operations
                if len(op_listSel) == 0:
                    # Selected is highlighted operation
                    op_listSel.append(op_hl)

                # Highlight closest operation
                op_hl = stat.get_closest_op(op_listSel)

                # Delete selected operations from statement
                self.STAT_del_op_list(stat, op_listSel)

                # Clear select operations
                op_listSel.clear()

            # Move selected operations
            elif key == "m":

                # If no selected operations
                if len(op_listSel) == 0:
                    # Selected is highlighted operation
                    op_listSel.append(op_hl)

                # Highlight closest operation
                op_hl = stat.get_closest_op(op_listSel)

                # Move selected operations from statement
                self.STAT_moveOps(stat, op_listSel)

                # Clear select operations
                op_listSel.clear()

            # Open highlighted operation
            elif key == "\n":

                op_curses = OperationCurses(op_hl)
                (is_edited, is_date_edited) = op_curses.browse(self.win_list[self.WIN_ID_INPUT])
                # If operation edited
                if is_edited:
                    stat.is_unsaved = True
                    # If date edited
                    if is_date_edited:
                        # Delete and insert opearion from/to statement
                        # To update index
                        stat.del_op_list([op_hl])
                        stat.insert_op(op_hl)

            # Duplicate highlighted operation
            elif key == "d":

                # Create new operation from highlighted one
                op_new = OperationCurses(op_hl.date, op_hl.mode, op_hl.tier,
                                   op_hl.cat, op_hl.desc, op_hl.amount)
                # Add new operation to statement
                stat.insert_op(op_new)
                # Highlight new operation
                op_hl = op_new

            # Save
            elif key == "s":
                stat.save()

            # Exit
            elif key == '\x1b':
                if stat.is_unsaved:
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
                        stat.save()
                    else:
                        win.addstr(4, 2, f"Discard changes",
                                   curses.color_pair(self.COLOR_PAIR_ID_RED_BLACK))
                        win.refresh()
                        time.sleep(1)
                        stat.reset()
                break

    def STAT_addOp(self, stat: Statement) -> None:

        # Create empty opeartion
        op = OperationCurses(datetime.now(), "", "", "", "", 0.0)

        # Use input window
        win = self.win_list[self.WIN_ID_INPUT]

        # For each operation field
        for field_idx in range(op.IDX_AMOUNT + 1):

            op.display(win, field_idx)
            (y, x) = (win.getyx()[0], 2)

            win.addstr(y, x, "Value : ")
            win.keypad(False)
            curses.echo()
            val_str = win.getstr().decode(encoding="utf-8")
            win.keypad(True)
            curses.noecho()

            if val_str != "":
                op.set_field(field_idx, val_str)

        stat.insert_op(op)

    def STAT_del_op_list(self, stat: Statement, op_list: List[OperationCurses]) -> None:

        # Use input window
        win = self.win_list[self.WIN_ID_INPUT]

        win.clear()
        win.border()
        win.addstr(0, 2, " DELETE OPERATIONS ", A_BOLD)
        win.addstr(2, 2, f"Delete {len(op_list)} operations")
        win.addstr(4, 2, "Confirm ? (y/n) : ")
        confirm_c = win.getch()
        if confirm_c != ord('y'):
            win.addstr(7, 2, f"Canceled", curses.color_pair(self.COLOR_PAIR_ID_RED_BLACK))
            win.refresh()
            time.sleep(1)
            return

        stat.del_op_list(op_list)

    def STAT_moveOps(self, statSrc: Statement, op_list: List[OperationCurses]) -> None:

        # Use input window
        win = self.win_list[self.WIN_ID_INPUT]

        win.clear()
        win.border()
        win.addstr(0, 2, " MOVE OPERATIONS ", A_BOLD)
        win.addstr(2, 2, f"Destination statement : ")
        win.addstr(3, 2, f"  Name (date) : ")
        curses.echo()
        stat_dst_name = win.getstr().decode(encoding="utf-8")
        curses.noecho()
        stat_dst = self.account.get_stat(stat_dst_name)
        if stat_dst is None:
            win.addstr(5, 2, f"Destination statement",
                       curses.color_pair(self.COLOR_PAIR_ID_RED_BLACK))
            win.addstr(6, 2, f"not found", curses.color_pair(self.COLOR_PAIR_ID_RED_BLACK))
            win.refresh()
            time.sleep(1)
            return

        win.clear()
        win.border()
        win.addstr(0, 2, " MOVE OPERATIONS ", A_BOLD)
        win.addstr(2, 2, f"Move {len(op_list)} operations")
        win.addstr(3, 2, f"To statement {stat_dst.name}")
        win.addstr(5, 2, "Confirm ? (y/n) : ")
        confirm_c = win.getch()
        if confirm_c != ord('y'):
            win.addstr(7, 2, f"Canceled", curses.color_pair(self.COLOR_PAIR_ID_RED_BLACK))
            win.refresh()
            time.sleep(1)
            return

        # For each operation
        for op in op_list:
            # Insert operation in target statement
            stat_dst.insert_op(op)
            # Delete operation from source statement
            statSrc.del_op_list([op])

        # Save source and destination statement
        statSrc.save()
        stat_dst.save()

if __name__ == "__main__":

    ACCOUNT = Account()

    # Curses
    DISPLAY = DisplayCurses(ACCOUNT)
    wrapper(DISPLAY.main)

    sys.exit(0)
