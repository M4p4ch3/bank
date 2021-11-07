"""
Display
"""

import curses
from curses import *
from datetime import datetime
from enum import IntEnum
import logging
from typing import (TYPE_CHECKING, List)

from ..account import Account
from ..statement import Statement
from ..operation import Operation
from ..utils.clipboard import Clipboard
from ..utils.my_date import FMT_DATE

if TYPE_CHECKING:
    from _curses import _CursesWindow
    Window = _CursesWindow
else:
    from typing import Any
    Window = Any

# Length for display padding
LEN_DATE = 10
LEN_NAME = LEN_DATE
LEN_MODE = 8
LEN_TIER = 18
LEN_CAT = 10
LEN_DESC = 34
LEN_AMOUNT = 8

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

class DispCurses():
    """
    Curses display
    """

    PADDING_Y = 0
    PADDING_X = 1
    BORDER_H = 1
    BORDER_W = BORDER_H

    def __init__(self, win_main: Window) -> None:

        # Windows list
        self.win_list: List[Window] = [None] * (WinId.LAST + 1)

        self.item_focus_idx: Statement | Operation = None

        self.item_hl: Statement | Operation = None

        self.item_list_sel: List[Statement | Operation] = []

        # Operations clipboard
        self.op_list_clipboard: Clipboard = Clipboard()

        # Main window
        (win_main_h, win_main_w) = win_main.getmaxyx()
        self.win_list[WinId.MAIN] = win_main

        # Sub main window
        win_h = win_main_h - 2 * self.BORDER_H - 2 * self.PADDING_Y
        win_w = int(2 * win_main_w / 3) - 2 * self.BORDER_W
        win_y = self.BORDER_H + self.PADDING_Y
        win_x = self.BORDER_W + self.PADDING_X
        win = curses.newwin(win_h, win_w, win_y, win_x)
        self.win_list[WinId.SUB] = win
        win_sub_h = win_h

        # Info window
        win_h = int(win_sub_h / 2) - int(self.PADDING_Y / 2)
        win_w = int(win_main_w / 3) - 2 * self.BORDER_W - self.PADDING_X
        win_y = self.BORDER_H + self.PADDING_Y
        win_x = win_main_w - self.BORDER_W - win_w - self.PADDING_X
        win = curses.newwin(win_h, win_w, win_y, win_x)
        self.win_list[WinId.INFO] = win

        # Input window
        win_h = int(win_sub_h / 2) - int(self.PADDING_Y / 2)
        win_w = int(win_main_w / 3) - 2 * self.BORDER_W - self.PADDING_X
        win_y = win_main_h - self.BORDER_H - win_h - self.PADDING_Y
        win_x = win_main_w - self.BORDER_W - win_w - self.PADDING_X
        win = curses.newwin(win_h, win_w, win_y, win_x)
        win.keypad(True)
        self.win_list[WinId.INPUT] = win

        curses.init_pair(ColorPairId.RED_BLACK, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(ColorPairId.GREEN_BLACK, curses.COLOR_GREEN, curses.COLOR_BLACK)

    def display():

        pass

class AccountDispCurses():
    """
    Curses account display
    """

    # Statement separator
    SEP_STAT = "|"
    SEP_STAT += "-" + "-".ljust(LEN_NAME, "-") + "-|"
    SEP_STAT += "-" + "-".ljust(LEN_DATE, "-") + "-|"
    SEP_STAT += "-" + "-".ljust(LEN_AMOUNT, "-") + "-|"
    SEP_STAT += "-" + "-".ljust(LEN_AMOUNT, "-") + "-|"
    SEP_STAT += "-" + "-".ljust(LEN_AMOUNT, "-") + "-|"
    SEP_STAT += "-" + "-".ljust(LEN_AMOUNT, "-") + "-|"

    # Statement missing
    MISS_STAT = "|"
    MISS_STAT += " " + "...".ljust(LEN_NAME, " ") + " |"
    MISS_STAT += " " + "...".ljust(LEN_DATE, " ") + " |"
    MISS_STAT += " " + "...".ljust(LEN_AMOUNT, " ") + " |"
    MISS_STAT += " " + "...".ljust(LEN_AMOUNT, " ") + " |"
    MISS_STAT += " " + "...".ljust(LEN_AMOUNT, " ") + " |"

    def __init__(self, account: Account, disp: DispCurses) -> None:

        self.logger = logging.getLogger("AccountDispCurses")

        # Account
        self.account: Account = account

        # Main display
        self.disp: DispCurses = disp

    def display(self, stat_first_idx: int, stat_hl: Statement) -> None:
        """
        Display
        """

        # Number of statements to display
        win_sub_h = self.disp.win_list[WinId.SUB].getmaxyx()[0]
        stat_disp_nb: int = win_sub_h - 4
        if len(self.account.stat_list) < stat_disp_nb:
            stat_disp_nb = len(self.account.stat_list)

        # Main window
        win: Window = self.disp.win_list[WinId.MAIN]

        # Border
        win.clear()
        win.border()
        win.move(0, 2)
        win.addstr(" STATEMENTS ", A_BOLD)

        # Status
        win_main_w = self.disp.win_list[WinId.MAIN].getmaxyx()[1]
        if self.account.is_unsaved:
            win.addstr(0, win_main_w - 10, "Unsaved",
                       curses.color_pair(ColorPairId.RED_BLACK))
        else:
            win.addstr(0, win_main_w - 10, "Saved",
                       curses.color_pair(ColorPairId.GREEN_BLACK))

        # Refresh
        win.refresh()

        # Use sub main window
        win: Window = self.disp.win_list[WinId.SUB]

        (win_y, win_x) = (0, 0)
        win.addstr(win_y, win_x, f"{self.SEP_STAT}")
        win_y = win_y + 1

        win.addstr(win_y, win_x, "| ")
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
        win_y = win_y + 1

        # Statement separator or missing
        if stat_first_idx == 0:
            win.addstr(win_y, win_x, self.SEP_STAT)
        else:
            win.addstr(win_y, win_x, self.MISS_STAT)
        win_y = win_y + 1

        # For each statement in display range
        # TODO
        # for stat_idx in range(stat_first_idx, stat_last_idx):
        stat_idx = stat_first_idx
        while stat_idx < len(self.account.stat_list) and stat_idx < stat_first_idx + stat_disp_nb:

            stat: Statement = self.account.stat_list[stat_idx]

            disp_flag = A_NORMAL
            if stat == stat_hl:
                disp_flag += A_STANDOUT

            win.addstr(win_y, win_x, "| ")
            win.addstr(stat.date.strftime(FMT_DATE).ljust(LEN_NAME), disp_flag)
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
                           curses.color_pair(ColorPairId.GREEN_BLACK))
            else:
                win.addstr(str(bal_diff).ljust(LEN_AMOUNT),
                           curses.color_pair(ColorPairId.RED_BLACK))
            win.addstr(" | ")
            bal_err = round(stat.bal_start + stat.op_sum - stat.bal_end, 2)
            if bal_err == 0.0:
                win.addstr(str(bal_err).ljust(LEN_AMOUNT),
                           curses.color_pair(ColorPairId.GREEN_BLACK))
            else:
                win.addstr(str(bal_err).ljust(LEN_AMOUNT),
                           curses.color_pair(ColorPairId.RED_BLACK))
            win.addstr(" |")
            win_y = win_y + 1

            stat_idx = stat_idx + 1

        # Statement separator or missing
        if stat_idx == len(self.account.stat_list):
            win.addstr(win_y, win_x, self.SEP_STAT)
        else:
            win.addstr(win_y, win_x, self.MISS_STAT)
        win_y = win_y + 1

        # Slider
        # Move to top right of table
        (win_y, win_x) = (3, win.getyx()[1])
        for _ in range(int(stat_first_idx * stat_disp_nb / len(self.account.stat_list))):
            win.addstr(win_y, win_x, " ")
            win_y = win_y + 1
        for _ in range(int(stat_disp_nb * stat_disp_nb / len(self.account.stat_list)) + 1):
            win.addstr(win_y, win_x, " ", A_STANDOUT)
            win_y = win_y + 1

        win.refresh()

    # TODO rework like operation.set_fields
    def add_stat(self) -> int:
        """
        Add statement
        """

        # Use input window
        win: Window = self.disp.win_list[WinId.INPUT]

        win.clear()
        win.border()
        win.move(0, 2)
        win.addstr(" STATEMENT ", A_BOLD)

        (win_y, win_x) = (2, 2)
        win.addstr(win_y, win_x, "date : ")
        win_y = win_y + 1
        win.addstr(win_y, win_x, "start balance : ")
        win_y = win_y + 1
        win.addstr(win_y, win_x, "end balance   : ")
        win_y = win_y + 1

        win.keypad(False)
        curses.echo()

        (win_y, win_x) = (2, 2)

        is_converted = False
        while not is_converted:
            win.addstr(win_y, win_x, "date :                  ")
            win.addstr(win_y, win_x, "date : ")
            val_str = win.getstr().decode(encoding="utf-8")
            try:
                date = datetime.strptime(val_str, FMT_DATE)
                is_converted = True
            except ValueError:
                pass

        win_y = win_y + 1

        is_converted = False
        while not is_converted:
            win.addstr(win_y, win_x, "start balance :         ")
            win.addstr(win_y, win_x, "start balance : ")
            val_str = win.getstr().decode(encoding="utf-8")
            try:
                bal_start = float(val_str)
                is_converted = True
            except ValueError:
                pass

        win_y = win_y + 1

        is_converted = False
        while not is_converted:
            win.addstr(win_y, win_x, "end balance :           ")
            win.addstr(win_y, win_x, "end balance : ")
            val_str = win.getstr().decode(encoding="utf-8")
            try:
                bal_end = float(val_str)
                is_converted = True
            except ValueError:
                pass

        win_y = win_y + 1

        win.keypad(True)
        curses.noecho()

        # Init statement
        stat = Statement(date.strftime(FMT_DATE), bal_start, bal_end)

        # Create statement file
        ret = stat.create_file()
        if ret != OK:
            self.logger.error("add_stat : Create statement file FAILED")
            return ret

        # Append statement to statements list
        self.account.insert_stat(stat)

        return OK

    def delete_stat(self, stat: Statement) -> None:
        """
        Delete statement
        """

        # Input window
        win: Window = self.disp.win_list[WinId.INPUT]
        win.clear()
        win.border()
        win.addstr(0, 2, " DELETE STATEMENT ", A_BOLD)
        win.addstr(2, 2, "Confirm ? (y/n) : ")
        confirm_c = win.getch()
        if confirm_c != ord('win_y'):
            win.addstr(7, 2, "Canceled", curses.color_pair(ColorPairId.RED_BLACK))
            win.refresh()
            return

        # Delete highlighted statement
        self.account.del_stat(stat)

    def browse(self) -> None:
        """
        Browse
        """

        win_sub_h = self.disp.win_list[WinId.SUB].getmaxyx()[0]

        # Index of first displayed statement
        stat_first_idx: int = 0

        # Highlighted statement
        stat_hl: Statement = None
        if len(self.account.stat_list) != 0:
            stat_hl = self.account.stat_list[0]

        while True:

            self.display(stat_first_idx, stat_hl)

            # # Command window
            # win: Window = self.disp.win_list[WinId.CMD]
            # win.clear()
            # win.border()
            # win.addstr(0, 2, " COMMANDS ", A_BOLD)
            # cmd_str = "Add : INS/+, Del : DEL/-"
            # cmd_str = cmd_str + ", Open : ENTER"
            # cmd_str = cmd_str + ", Save : S, Ret : ESCAPE"
            # win.addstr(1, 2, cmd_str)
            # win.refresh()

            self.disp.win_list[WinId.SUB].keypad(True)
            key = self.disp.win_list[WinId.SUB].getkey()

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
                if stat_hl_idx - stat_first_idx >= win_sub_h - 4:
                    # Next page
                    stat_first_idx = stat_first_idx + 1
                    if stat_first_idx > len(self.account.stat_list) - (win_sub_h - 4):
                        stat_first_idx = len(self.account.stat_list) - (win_sub_h - 4)

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
                elif stat_hl_idx >= stat_first_idx + win_sub_h - 4:
                    stat_hl = self.account.stat_list[stat_first_idx + win_sub_h - 4 - 1]

            # Next page
            elif key == "KEY_NPAGE":

                # Next page
                stat_first_idx = stat_first_idx + 3
                if stat_first_idx > len(self.account.stat_list) - (win_sub_h - 4):
                    stat_first_idx = len(self.account.stat_list) - (win_sub_h - 4)
                    if stat_first_idx < 0:
                        stat_first_idx = 0

                # If out of display range
                stat_hl_idx = self.account.stat_list.index(stat_hl)
                if stat_hl_idx < stat_first_idx:
                    stat_hl = self.account.stat_list[stat_first_idx]
                elif stat_hl_idx >= stat_first_idx + win_sub_h - 4:
                    stat_hl = self.account.stat_list[stat_first_idx + win_sub_h - 4 - 1]

            # Add statement
            elif key in ("KEY_IC", "+"):
                self.add_stat()

            # Delete highlighted statement
            elif key in ("KEY_DC", "-"):
                self.delete_stat(stat_hl)
                # Reset highlighted statement
                stat_hl = self.account.stat_list[0]

            # Open highligthed statement
            elif key == "\n":
                # Init highligthed statement display
                stat_disp: StatementDispCurses = StatementDispCurses(stat_hl, self.disp)
                # Browse highligthed statement
                stat_disp.browse()

            elif key == "s":
                self.account.export_file()

            elif key == '\x1b':
                if self.account.is_unsaved:
                    # Input window
                    win: Window = self.disp.win_list[WinId.INPUT]
                    win.clear()
                    win.border()
                    win.addstr(0, 2, " UNSAVED CHANGES ", A_BOLD)
                    win.addstr(2, 2, "Save ? (y/n) : ")
                    save_c = win.getch()
                    if save_c != ord('n'):
                        win.addstr(4, 2, "Saving")
                        win.refresh()
                        self.account.export_file()
                    else:
                        win.addstr(4, 2, "Discard changes",
                                   curses.color_pair(ColorPairId.RED_BLACK))
                        win.refresh()
                break

class StatementDispCurses():
    """
    Curses statetement display
    """

    # Operation separator
    OP_SEP = "|"
    OP_SEP += "-" + "-".ljust(LEN_DATE, "-") + "-|"
    OP_SEP += "-" + "-".ljust(LEN_MODE, "-") + "-|"
    OP_SEP += "-" + "-".ljust(LEN_TIER, "-") + "-|"
    OP_SEP += "-" + "-".ljust(LEN_CAT, "-") + "-|"
    OP_SEP += "-" + "-".ljust(LEN_DESC, "-") + "-|"
    OP_SEP += "-" + "-".ljust(LEN_AMOUNT, "-") + "-|"

    # Operation header
    OP_HEADER = "|"
    OP_HEADER += " " + "date".ljust(LEN_DATE, " ") + " |"
    OP_HEADER += " " + "mode".ljust(LEN_MODE, " ") + " |"
    OP_HEADER += " " + "tier".ljust(LEN_TIER, " ") + " |"
    OP_HEADER += " " + "cat".ljust(LEN_CAT, " ") + " |"
    OP_HEADER += " " + "desc".ljust(LEN_DESC, " ") + " |"
    OP_HEADER += " " + "amount".ljust(LEN_AMOUNT, " ") + " |"

    # Missing operation
    OP_MISS = "|"
    OP_MISS += " " + "...".ljust(LEN_DATE, ' ') + " |"
    OP_MISS += " " + "...".ljust(LEN_MODE, ' ') + " |"
    OP_MISS += " " + "...".ljust(LEN_TIER, ' ') + " |"
    OP_MISS += " " + "...".ljust(LEN_CAT, ' ') + " |"
    OP_MISS += " " + "...".ljust(LEN_DESC, ' ') + " |"
    OP_MISS += " " + "...".ljust(LEN_AMOUNT, ' ') + " |"

    def __init__(self, stat: Statement, disp: DispCurses) -> None:

        # Statement
        self.stat: Statement = stat

        # Main display
        self.disp: DispCurses = disp

        # Index of focused operation
        # Index of first displayed operation
        self.op_focus_idx: int = 0

        # Highlighted operation
        self.op_hl: Operation = None

        # Selected operations list
        self.op_sel_list: List[Operation] = []

    def display_op_list(self, is_hl_updated: bool, is_focus_updated: bool) -> None:
        """
        Display operations list
        """

        # Sub main window
        win_sub: Window = self.disp.win_list[WinId.SUB]
        win_sub_h: int = win_sub.getmaxyx()[0]

        # Number of displayed operations
        op_disp_nb: int = win_sub_h - 4
        if len(self.stat.op_list) < op_disp_nb:
            op_disp_nb = len(self.stat.op_list)

        # If highlighted operation updated
        if is_hl_updated:

            # Fix focus

            op_hl_idx = self.stat.op_list.index(self.op_hl)

            if op_hl_idx < self.op_focus_idx:

                # Move focus up
                self.op_focus_idx -= 1
                if self.op_focus_idx < 0:
                    self.op_focus_idx = 0

            elif op_hl_idx > self.op_focus_idx + op_disp_nb - 1:

                # Move focus down
                self.op_focus_idx += 1
                if self.op_focus_idx > len(self.stat.op_list) - op_disp_nb:
                    self.op_focus_idx = len(self.stat.op_list) - op_disp_nb

        # Else, if focus updated
        elif is_focus_updated:

            # Fix focus

            if self.op_focus_idx < 0:
                self.op_focus_idx = 0
            elif self.op_focus_idx > len(self.stat.op_list) - op_disp_nb:
                self.op_focus_idx = len(self.stat.op_list) - op_disp_nb

            # Fix highlighted operation

            op_hl_idx = self.stat.op_list.index(self.op_hl)

            if op_hl_idx < self.op_focus_idx:

                # Highlight first displayed operation
                op_hl_idx = self.op_focus_idx
                self.op_hl = self.stat.op_list[op_hl_idx]

            elif op_hl_idx > self.op_focus_idx + op_disp_nb - 1:

                # Highlight last displayed operation
                op_hl_idx = self.op_focus_idx + op_disp_nb - 1
                self.op_hl = self.stat.op_list[op_hl_idx]

        (win_y, win_x) = (0, 0)

        # Operation separator
        win_sub.addstr(win_y, win_x, self.OP_SEP)
        win_y += 1

        # Operations header
        win_sub.addstr(win_y, win_x, self.OP_HEADER)
        win_y += 1

        if len(self.stat.op_list) == 0:
            win_sub.addstr(win_y, win_x, self.OP_SEP)
            win_y += 1
            win_sub.addstr(win_y, win_x, self.OP_SEP)
            win_y += 1
            win_sub.refresh()
            return

        # Operation separator or missing
        if self.op_focus_idx == 0:
            win_sub.addstr(win_y, win_x, self.OP_SEP)
        else:
            win_sub.addstr(win_y, win_x, self.OP_MISS)
        win_y += 1

        # Operations list
        for op_idx in range(self.op_focus_idx, self.op_focus_idx + op_disp_nb):

            if op_idx >= len(self.stat.op_list):
                break

            operation = self.stat.op_list[op_idx]

            disp_flag = A_NORMAL
            if operation == self.op_hl:
                disp_flag += A_STANDOUT
            if operation in self.op_sel_list:
                disp_flag += A_BOLD

            op_str = "|"
            op_str += " " + operation.date.strftime(FMT_DATE)[:LEN_DATE].ljust(LEN_DATE, ' ') + " |"
            op_str += " " + operation.mode.ljust(LEN_MODE, ' ') + " |"
            op_str += " " + operation.tier[:LEN_TIER].ljust(LEN_TIER, ' ') + " |"
            op_str += " " + operation.cat[:LEN_CAT].ljust(LEN_CAT, ' ') + " |"
            op_str += " " + operation.desc[:LEN_DESC].ljust(LEN_DESC, ' ') + " |"
            op_str += " " + str(operation.amount)[:LEN_AMOUNT].ljust(LEN_AMOUNT, ' ') + " |"
            win_sub.addstr(win_y, win_x, op_str, disp_flag)
            win_y += 1

        # Operation separator or missing
        if op_idx == len(self.stat.op_list) - 1:
            win_sub.addstr(win_y, win_x, self.OP_SEP)
        else:
            win_sub.addstr(win_y, win_x, self.OP_MISS)
        win_y += 1

        if len(self.stat.op_list) != 0:
            op_disp_ratio = op_disp_nb / len(self.stat.op_list)

        # Slider
        (win_y, win_x) = (3, win_sub.getyx()[1])
        for _ in range(0, int(self.op_focus_idx * op_disp_ratio)):
            win_sub.addstr(win_y, win_x, " ")
            win_y += 1
        for _ in range(int(self.op_focus_idx * op_disp_ratio),
                       int((self.op_focus_idx + op_disp_nb) * op_disp_ratio)):
            win_sub.addstr(win_y, win_x, " ", A_STANDOUT)
            win_y += 1
        for _ in range(int((self.op_focus_idx + op_disp_nb) * op_disp_ratio),
                       int((len(self.stat.op_list)) * op_disp_ratio)):
            win_sub.addstr(win_y, win_x, " ")
            win_y += 1

        win_sub.refresh()

    def display_info(self) -> None:
        """
        Display statement info
        """

        # Info window
        win_info: Window = self.disp.win_list[WinId.INFO]

        win_info.clear()
        win_info.border()
        win_info.addstr(0, 2, " INFO ", A_BOLD)

        (win_y, win_x) = (2, 2)
        win_info.addstr(win_y, win_x, f"date : {self.stat.date.strftime(FMT_DATE)}")
        win_y += 1

        win_info.addstr(win_y, win_x, f"balance start : {self.stat.bal_start}")
        win_y += 1

        win_info.addstr(win_y, win_x, f"balance end : {self.stat.bal_end}")
        win_y += 1

        bal_diff = round(self.stat.bal_end - self.stat.bal_start, 2)
        win_info.addstr(win_y, win_x, "balance diff : ")
        if bal_diff >= 0.0:
            win_info.addstr(str(bal_diff), curses.color_pair(ColorPairId.GREEN_BLACK))
        else:
            win_info.addstr(str(bal_diff), curses.color_pair(ColorPairId.RED_BLACK))
        win_y += 1

        win_info.addstr(win_y, win_x,
                        f"actual end : {(self.stat.bal_start + self.stat.op_sum):.2f}")
        win_y += 1

        bal_err = round(self.stat.bal_start + self.stat.op_sum - self.stat.bal_end, 2)
        win_info.addstr(win_y, win_x, "balance error : ")
        if bal_err == 0.0:
            win_info.addstr(str(bal_err), curses.color_pair(ColorPairId.GREEN_BLACK))
        else:
            win_info.addstr(str(bal_err), curses.color_pair(ColorPairId.RED_BLACK))
        win_y += 1

        win_info.addstr(win_y, win_x, "status : ")
        if self.stat.is_unsaved:
            win_info.addstr("Unsaved", curses.color_pair(ColorPairId.RED_BLACK))
        else:
            win_info.addstr("Saved", curses.color_pair(ColorPairId.GREEN_BLACK))
        win_y += 1

        win_info.addstr(win_y, win_x,
                        f"clipboard : {self.disp.op_list_clipboard.get_len()} operations")
        win_y += 1

        win_info.refresh()

    # def display_commands(self) -> None:

    #     win: Window = self.disp.win_list[WinId.CMD]
    #     win.clear()
    #     win.border()
    #     win.addstr(0, 2, " COMMANDS ", A_BOLD)
    #     cmd_str = "Add : INS/+, Del : DEL/-"
    #     cmd_str = cmd_str + ", Dupl : D, (Un)sel : SPACE, Move : M "
    #     cmd_str = cmd_str + ", Open : ENTER"
    #     cmd_str = cmd_str + ", Save : S, Ret : ESCAPE"
    #     win.addstr(1, 2, cmd_str)
    #     win.refresh()

    def copy_op_list(self) -> None:
        """
        Copy selected operations

        Set clipboard to selected operations
        """

        if len(self.op_sel_list) > 0:
            op_list = self.op_sel_list
        elif self.op_hl is not None:
            op_list = [self.op_hl]
        else:
            return

        self.disp.op_list_clipboard.set(op_list)

    def cut_op_list(self) -> None:
        """
        Cut selected operations

        Set clipboard to selected operations
        Delete from statement
        """

        if len(self.op_sel_list) > 0:
            op_list = self.op_sel_list
        elif self.op_hl is not None:
            op_list = [self.op_hl]
        else:
            return

        self.disp.op_list_clipboard.set(op_list)

        # If highlighted operation in buffer
        if self.op_hl in op_list:
            # Highlight closest opeartion
            self.op_hl = self.stat.get_closest_op(op_list)

        # Delete operations from statement
        self.stat.del_op_list(op_list)

    def paste_op_list(self) -> None:
        """
        Paste operations
        """

        op_list = self.disp.op_list_clipboard.get()
        if op_list is None or len(op_list) == 0:
            return

        for operation in op_list:

            # Deep copy
            op_new = operation.copy()

            # Insert new operation in statement
            self.stat.insert_op(op_new)

    def browse_op(self) -> None:
        """
        Browse highlighted operation
        """

        # Browse highlighted operation
        op_disp: OperationDispCurses = OperationDispCurses(
            self.op_hl, self.disp.win_list[WinId.INPUT])
        (is_edited, is_date_edited) = op_disp.browse()

        # If operation edited
        if is_edited:

            self.stat.is_unsaved = True

            # If date edited
            if is_date_edited:

                # Re-insert opearation in statement to update index
                self.stat.del_op_list([self.op_hl])
                self.stat.insert_op(self.op_hl)

    def add_op(self) -> None:
        """
        Add operation
        """

        # Create empty operation
        operation = Operation(datetime.now(), "", "", "", "", 0.0)

        # Set operation fields using display
        op_disp: OperationDispCurses = OperationDispCurses(
            operation, self.disp.win_list[WinId.INPUT])
        op_disp.set_fields()

        # Insert new operation
        self.stat.insert_op(operation)

    def delete_op(self) -> None:
        """
        Delete highlighted operation or selected operations list
        """

        # Operations delete list : Selected operations
        op_del_list = self.op_sel_list
        # If no selected operations
        if len(self.op_sel_list) == 0:
            # Operations delete list : Highlighted operation
            op_del_list = [self.op_hl]

        # If highlighted operation in buffer
        if self.op_hl in op_del_list:
            # Highlight closest opeartion
            self.op_hl = self.stat.get_closest_op(op_del_list)

        # Use input window
        win = self.disp.win_list[WinId.INPUT]
        win.clear()
        win.border()
        win.addstr(0, 2, " DELETE OPERATIONS ", A_BOLD)
        win.addstr(2, 2, f"Delete {len(op_del_list)} operations")
        win.addstr(4, 2, "Confirm ? (y/n) : ")
        confirm_c = win.getch()
        if confirm_c != ord('y'):
            win.addstr(7, 2, "Canceled", curses.color_pair(ColorPairId.RED_BLACK))
            win.refresh()
            return

        # Delete operations from statement
        self.stat.del_op_list(op_del_list)

        # Clear selected operations
        self.op_sel_list.clear()

    def exit(self) -> None:
        """
        Exit statement browse
        """

        # Check if unsaved changes
        if self.stat.is_unsaved:

            # Unsaved changes

            # Input window, ask for save
            win: Window = self.disp.win_list[WinId.INPUT]
            win.clear()
            win.border()
            win.addstr(0, 2, " UNSAVED CHANGES ", A_BOLD)
            win.addstr(2, 2, "Save ? (y/n) : ")
            save_c = win.getch()

            # If not 'n'
            if save_c != ord('n'):

                # Save changes
                win.addstr(4, 2, "Saving")
                win.refresh()
                self.stat.export_file()

            # Else, 'n'
            else:

                # Discard changes
                win.addstr(4, 2, "Discard changes",
                           curses.color_pair(ColorPairId.RED_BLACK))
                win.refresh()
                self.stat.import_file()

    def browse(self) -> None:
        """
        Browse
        """

        # Init
        self.op_focus_idx: int = 0
        if len(self.stat.op_list) != 0:
            self.op_hl = self.stat.op_list[0]
        else:
            self.op_hl = None
        self.op_sel_list = []

        # Main window
        win_main: Window = self.disp.win_list[WinId.MAIN]
        win_main.clear()
        win_main.border()
        win_main.move(0, 2)
        win_main.addstr(" STATEMENT ", A_BOLD)
        win_main.refresh()

        # Display statement info
        self.display_info()

        # Display commands
        # self.display_commands()

        # Display operations list
        self.display_op_list(False, False)

        while True:

            info_updated = False
            is_hl_updated = False
            is_focus_updated = False

            key = self.disp.win_list[WinId.MAIN].getkey()

            # Highlight previous operation
            if key == "KEY_UP":
                if self.op_hl is None:
                    continue
                op_hl_idx = self.stat.op_list.index(self.op_hl) - 1
                if op_hl_idx < 0:
                    op_hl_idx = 0
                    continue
                self.op_hl = self.stat.op_list[op_hl_idx]
                is_hl_updated = True

            # Highlight next operation
            elif key == "KEY_DOWN":
                if self.op_hl is None:
                    continue
                op_hl_idx = self.stat.op_list.index(self.op_hl) + 1
                if op_hl_idx >= len(self.stat.op_list):
                    op_hl_idx = len(self.stat.op_list) - 1
                    continue
                self.op_hl = self.stat.op_list[op_hl_idx]
                is_hl_updated = True

            # Focus previous operations
            elif key == "KEY_PPAGE":
                if self.op_hl is None:
                    continue
                self.op_focus_idx -= 3
                is_focus_updated = True

            # Focus next operations
            elif key == "KEY_NPAGE":
                if self.op_hl is None:
                    continue
                self.op_focus_idx += 3
                is_focus_updated = True

            # Trigger operation selection
            elif key == " ":
                if self.op_hl is None:
                    continue
                if self.op_hl not in self.op_sel_list:
                    self.op_sel_list.append(self.op_hl)
                else:
                    self.op_sel_list.remove(self.op_hl)

            # Copy operations(s)
            elif key == "c":
                self.copy_op_list()
                info_updated = True

            # Cut operation(s)
            elif key == "x":
                self.cut_op_list()
                info_updated = True

            # Paste operation(s)
            elif key == "v":
                self.paste_op_list()
                info_updated = True

            # Open highlighted operation
            elif key == "\n":
                self.browse_op()
                info_updated = True

            # Add operation
            elif key in ("KEY_IC", "+"):
                self.add_op()
                info_updated = True

            # Delete operation(s)
            elif key in ("KEY_DC", "-"):
                self.delete_op()
                info_updated = True

            # Save
            elif key == "s":
                self.stat.export_file()
                info_updated = True

            # Exit
            elif key == '\x1b':
                self.exit()
                break

            if info_updated:
                # Display statement info
                self.display_info()

            # Display commands
            # self.display_commands()

            # Display operations list
            self.display_op_list(is_hl_updated, is_focus_updated)

class OperationDispCurses():
    """
    Curses operation display
    """

    def __init__(self, operation: Operation, win: Window) -> None:

        # Operation
        self.operation: Operation = operation

        # Window
        self.win: Window = win

        # Index of operation highlighted field
        self.op_field_hl_idx = 0

    def display(self):
        """
        Display
        """

        # Window border
        self.win.clear()
        self.win.border()
        self.win.move(0, 2)
        self.win.addstr(" OPERATION ", A_BOLD)

        # Init window cursor position
        (win_y, win_x) = (2, 2)

        # For each field
        for field_idx in range(self.operation.IDX_AMOUNT + 1):

            # Set display flag for highlighted field
            disp_flag = A_NORMAL
            if field_idx == self.op_field_hl_idx:
                disp_flag = A_STANDOUT

            # Display field
            (name_str, val_str) = self.operation.get_field(field_idx)
            self.win.addstr(win_y, win_x, f"{name_str} : {val_str}", disp_flag)

            # Update window cursor position
            win_y = win_y + 1

        # Move cursor away from last field
        win_y = win_y + 1
        self.win.addstr(win_y, win_x, "")

        self.win.refresh()

    def browse(self):
        """
        Browse
        """

        self.win.keypad(True)

        self.op_field_hl_idx = 0

        # Is operation edited
        is_edited = False

        # Is operation date edited
        is_date_edited = False

        while True:

            # Display
            self.display()

            # Get key
            key = self.win.getkey()

            # Highlight previous field
            if key == "KEY_UP":
                self.op_field_hl_idx -= 1
                if self.op_field_hl_idx < self.operation.IDX_DATE:
                    self.op_field_hl_idx = self.operation.IDX_AMOUNT

            # Highlight next field
            elif key == "KEY_DOWN":
                self.op_field_hl_idx += 1
                if self.op_field_hl_idx > self.operation.IDX_AMOUNT:
                    self.op_field_hl_idx = self.operation.IDX_DATE

            # Edit highlighted field
            elif key == "\n":

                # Field value edit prompt
                self.win.addstr("Value : ")

                # Get field value input
                self.win.keypad(False)
                curses.echo()
                val_str = self.win.getstr().decode(encoding="utf-8")
                self.win.keypad(True)
                curses.noecho()

                # If field value input
                if val_str != "":

                    # Set field value
                    is_edited_single = self.operation.set_field(self.op_field_hl_idx, val_str)
                    if is_edited_single:
                        is_edited = True
                        if self.op_field_hl_idx == self.operation.IDX_DATE:
                            is_date_edited = True

            # Exit
            elif key == '\x1b':
                break

        return (is_edited, is_date_edited)

    def set_fields(self) -> None:
        """
        Iterate over fields and set
        """

        self.win.keypad(True)

        # For each field
        for field_idx in range(self.operation.IDX_AMOUNT + 1):

            # Highlight current field
            self.op_field_hl_idx = field_idx

            # Display
            self.display()
            (win_y, win_x) = (self.win.getyx()[0], 2)

            # Get value
            self.win.addstr(win_y, win_x, "Value : ")
            self.win.keypad(False)
            curses.echo()
            val_str = self.win.getstr().decode(encoding="utf-8")
            self.win.keypad(True)
            curses.noecho()

            # Set value
            if val_str != "":
                self.operation.set_field(field_idx, val_str)
