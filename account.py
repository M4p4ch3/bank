"""
Account
"""

import csv
from datetime import datetime
import logging
from typing import (TYPE_CHECKING, List)

from statement import (Statement, StatementDispMgrCurses)
from utils import (LEN_DATE, LEN_NAME, LEN_AMOUNT,
                   FMT_DATE,
                   WinId, ColorPairId, Clipboard)

# Display
import curses
from curses import *

if TYPE_CHECKING:
    from _curses import _CursesWindow
    Window = _CursesWindow
else:
    from typing import Any
    Window = Any

class Account():
    """
    Account
    """

    def __init__(self) -> None:

        self.log = logging.getLogger("Account")

        self.file_path = "statements.csv"

        # Statements list
        self.stat_list: List[Statement] = list()

        # Import statements from file
        self.import_file()

        self.is_unsaved: bool = False

    def get_str(self, indent: int = 0) -> str:
        """
        Get string representation
        """

        indent_str = ""
        for _ in range(indent):
            indent_str += "    "

        ret = ""
        ret += f"{indent_str}statements : [\n"
        for stat in self.stat_list:
            ret += f"{indent_str}    {{\n"
            ret += stat.get_str(indent + 2) + "\n"
            ret += f"{indent_str}    }}\n"
        ret += f"{indent_str}]"

        return ret

    def get_stat(self, stat_name: str) -> Statement:
        """
        Get statement by name
        """

        for stat in self.stat_list:
            if stat.name == stat_name:
                return stat

        return None

    def import_file(self) -> None:
        """
        Import statements from file
        """

        try:
            # Open statements CSV file
            file = open(self.file_path, "r", encoding="utf8")
        except FileNotFoundError:
            self.log.error("Account.import_file ERROR : Open statements CSV file FAILED")
            return

        file_csv = csv.reader(file)

        # For each statement line
        for stat_line in file_csv:

            # Create statement
            stat = Statement(stat_line[Statement.IDX_DATE],
                             float(stat_line[Statement.IDX_BAL_START]),
                             float(stat_line[Statement.IDX_BAL_END]))

            # Add statement to statements list
            self.stat_list.append(stat)

        file.close()

    def export_file(self):
        """
        Export statements to file
        """

        try:
            # Open statements CSV file
            file = open(self.file_path, "w", encoding="utf8")
        except FileNotFoundError:
            self.log.error("Account.export_file ERROR : Open statements CSV file FAILED")
            return

        file_csv = csv.writer(file, delimiter=',', quotechar='"')

        # For each statement
        for stat in self.stat_list:

            # Create statement line
            stat_csv = [stat.name, str(stat.bal_start), str(stat.bal_end)]

            # Write statement line to CSV file
            file_csv.writerow(stat_csv)

        self.is_unsaved = False

        file.close()

    def insert_stat(self, stat: Statement) -> None:
        """
        Insert statement
        """

        # Find index
        idx = 0
        while idx < len(self.stat_list) and stat.date > self.stat_list[idx].date:
            idx = idx + 1

        # Insert statement at dedicated index
        self.stat_list.insert(idx, stat)

        self.is_unsaved = True

    def del_stat(self, stat: Statement) -> None:
        """
        Delete statement
        """

        if stat not in self.stat_list:
            return

        self.stat_list.remove(stat)

        self.is_unsaved = True

class AccountDispMgrCurses():
    """
    Curses account display manager
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

    def __init__(self, account: Account, win_list: List[Window],
                 op_list_buffer: Clipboard) -> None:

        # Account
        self.account: Account = account

        # Windows list
        self.win_list: List[Window] = win_list

        # Operations list buffer
        self.op_list_buffer: Clipboard = op_list_buffer

    def display(self, stat_first_idx: int, stat_hl: Statement) -> None:
        """
        Display
        """

        # Number of statements to display
        win_sub_h = self.win_list[WinId.SUB].getmaxyx()[0]
        stat_disp_nb: int = win_sub_h - 4
        if len(self.account.stat_list) < stat_disp_nb:
            stat_disp_nb = len(self.account.stat_list)

        # Main window
        win: Window = self.win_list[WinId.MAIN]

        # Border
        win.clear()
        win.border()
        win.move(0, 2)
        win.addstr(" STATEMENTS ", A_BOLD)

        # Status
        win_main_w = self.win_list[WinId.MAIN].getmaxyx()[1]
        if self.account.is_unsaved:
            win.addstr(0, win_main_w - 10, "Unsaved",
                curses.color_pair(ColorPairId.RED_BLACK))
        else:
            win.addstr(0, win_main_w - 10, "Saved",
                curses.color_pair(ColorPairId.GREEN_BLACK))

        # Refresh
        win.refresh()

        # Use sub main window
        win: Window = self.win_list[WinId.SUB]

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

    def add_stat(self) -> None:
        """
        Add statement
        """

        # Use input window
        win: Window = self.win_list[WinId.INPUT]

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

        # Create statement
        # Statement CSV file does not exit
        # Import will create it
        stat = Statement(date.strftime(FMT_DATE), bal_start, bal_end)

        # Append statement to statements list
        self.account.insertStat(stat)

    def delete_stat(self, stat: Statement) -> None:
        """
        Delete statement
        """

        # Input window
        win: Window = self.win_list[WinId.INPUT]
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

        win_sub_h = self.win_list[WinId.SUB].getmaxyx()[0]

        # Index of first displayed statement
        stat_first_idx: int = 0

        # Highlighted statement
        stat_hl: Statement = None
        if len(self.account.stat_list) != 0:
            stat_hl = self.account.stat_list[0]

        while True:

            self.display(stat_first_idx, stat_hl)

            # # Command window
            # win: Window = self.win_list[WinId.CMD]
            # win.clear()
            # win.border()
            # win.addstr(0, 2, " COMMANDS ", A_BOLD)
            # cmd_str = "Add : INS/+, Del : DEL/-"
            # cmd_str = cmd_str + ", Open : ENTER"
            # cmd_str = cmd_str + ", Save : S, Ret : ESCAPE"
            # win.addstr(1, 2, cmd_str)
            # win.refresh()

            self.win_list[WinId.SUB].keypad(True)
            key = self.win_list[WinId.SUB].getkey()

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
                stat_disp_mgr: StatementDispMgrCurses = StatementDispMgrCurses(
                    stat_hl, self.win_list, self.op_list_buffer)
                stat_disp_mgr.browse()

            elif key == "s":
                self.account.export_file()

            elif key == '\x1b':
                if self.account.is_unsaved:
                    # Input window
                    win: Window = self.win_list[WinId.INPUT]
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
