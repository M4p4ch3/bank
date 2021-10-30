
"""
Account
"""

import csv
import logging
import time
from typing import (TYPE_CHECKING, List, Tuple)

from utils import (OK, ERROR,
                   LEN_DATE, LEN_NAME, LEN_MODE, LEN_TIER, LEN_CAT, LEN_DESC, LEN_AMOUNT,
                   FMT_DATE)
from statement import Statement
from operation import Operation

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

        status: int = OK

        self.log = logging.getLogger("Account")

        self.file_path = "statements.csv"

        # Statements list
        self.stat_list: List[Statement] = list()

        # Read statements
        status = self.read()
        if status != OK:
            self.log.error("Account.__init__ ERROR : Read statements FAILED")

        # Operations buffer list
        self.op_buffer_list = list()

        # Display manager
        self.disp_mgr: AccountDispMgrCurses = AccountDispMgrCurses(self)

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

    def read(self) -> int:
        """
        Read from file
        """

        try:
            # Open statements CSV file
            file = open(self.file_path, "r")
        except FileNotFoundError:
            self.log.error("Account.read ERROR : Open statements CSV file FAILED")
            return ERROR

        file_csv = csv.reader(file)

        # For each statement line
        for stat_line in file_csv:

            # Create and read statement
            stat = Statement(stat_line[Statement.IDX_DATE],
                             float(stat_line[Statement.IDX_BAL_START]),
                             float(stat_line[Statement.IDX_BAL_END]),
                             self)
            stat.read()

            # Add statement to statements list
            self.stat_list.append(stat)

        file.close()

        return OK

    def write(self) -> int:
        """
        Write to CSV file
        """

        try:
            # Open statements CSV file
            file = open(self.file_path, "w")
        except FileNotFoundError:
            self.log.error("Account.write ERROR : Open statements CSV file FAILED")
            return ERROR

        file_csv = csv.writer(file, delimiter=',', quotechar='"')

        # For each statement
        for stat in self.stat_list:

            # Create statement line
            stat_csv = [stat.name, str(stat.bal_start), str(stat.bal_end)]

            try:
                # Write statement line to CSV file
                file_csv.writerow(stat_csv)
            # TODO add error type
            except:
                self.log.error("Account.write ERROR : Write statement line to CSV file FAILED")
                return ERROR

        self.is_unsaved = False

        file.close()

        return OK

    def reset(self) -> int:
        """
        Reset : Read
        """

        status: int = OK

        # Read statements
        status = self.read()
        if status != OK:
            self.log.error("Account.reset ERROR : Read statements FAILED")
            return ERROR

        return OK

    def save(self) -> int:
        """
        Save : Write
        """

        status: int = OK

        # Write statements
        status = self.write()
        if status != OK:
            self.log.error("Account.save ERROR : Write statements FAILED")
            return ERROR

        return OK

    def insert_stat(self, stat: Statement) -> int:
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

        return OK

    def del_stat(self, stat: Statement) -> int:
        """
        Delete statement
        """

        try:
            self.stat_list.remove(stat)
        # TODO add error type
        except:
            self.log.error("Account.del_stat ERROR : Statement not found")
            return ERROR

        self.is_unsaved = True

        return OK

    def clear_op_buffer(self) -> None:
        """
        Clear operations buffer
        """

        self.op_buffer_list.clear()

    def set_op_buffer(self, op_list: List[Operation]) -> None:
        """
        Set operations in buffer

        Args:
            op_list (List[Operation]): Operations list to set in buffer
        """

        self.clear_op_buffer()
        for op in op_list:
            # Deep copy
            op_new = op.copy()
            self.op_buffer_list.append(op_new)

    def get_op_buffer(self) -> List[Operation]:
        """
        Get operations from buffer

        Returns:
            List[Operation]: Operations in buffer
        """
        
        return self.op_buffer_list

class AccountDispMgrCurses():
    """
    Curses account display manager
    """

    # Color pair ID
    COLOR_PAIR_ID_RED_BLACK = 1
    COLOR_PAIR_ID_GREEN_BLACK = 2

    # Window ID
    WIN_ID_MAIN = 0
    WIN_ID_SUB = 1
    WIN_ID_INFO = 2
    WIN_ID_INPUT = 3
    WIN_ID_LAST = WIN_ID_INPUT

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

    def __init__(self, account: Account) -> None:

        self.account: Account = account

    def display(self, stat_first_idx: int, stat_hl: Statement) -> None:

        # Number of statements to display
        win_sub_h = self.win_list[self.WIN_ID_SUB].getmaxyx()[0]
        stat_disp_nb: int = win_sub_h - 4
        if len(self.account.stat_list) < stat_disp_nb:
            stat_disp_nb = len(self.account.stat_list)
        # TODO
        # stat_last_idx

        # Main window
        win: Window = self.win_list[self.WIN_ID_MAIN]

        # Border
        win.clear()
        win.border()
        win.move(0, 2)
        win.addstr(" STATEMENTS ", A_BOLD)

        # Status
        win_main_w = self.win_list[self.WIN_ID_MAIN].getmaxyx()[1]
        if self.account.is_unsaved:
            win.addstr(0, win_main_w - 10, "Unsaved", curses.color_pair(self.COLOR_PAIR_ID_RED_BLACK))
        else:
            win.addstr(0, win_main_w - 10, "Saved", curses.color_pair(self.COLOR_PAIR_ID_GREEN_BLACK))

        # Refresh
        win.refresh()

        # Use sub main window
        win: Window = self.win_list[self.WIN_ID_SUB]

        (y, x) = (0, 0)
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
        (y, x) = (3, win.getyx()[1])
        for _ in range(int(stat_first_idx * stat_disp_nb / len(self.account.stat_list))):
            win.addstr(y, x, " ")
            y = y + 1
        for _ in range(int(stat_disp_nb * stat_disp_nb / len(self.account.stat_list)) + 1):
            win.addstr(y, x, " ", A_STANDOUT)
            y = y + 1

        win.refresh()

    def add_stat(self) -> None:

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

    def delete_stat(self, stat: Statement) -> None:

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

    def browse(self, win_list: List[Window]) -> None:

        self.win_list = win_list

        win_sub_h = self.win_list[self.WIN_ID_SUB].getmaxyx()[0]

        # Index of first displayed statement
        stat_first_idx: int = 0

        # Highlighted statement
        stat_hl: Statement = None
        if len(self.account.stat_list) != 0:
            stat_hl = self.account.stat_list[0]

        while True:

            self.display(stat_first_idx, stat_hl)

            # # Command window
            # win: Window = self.win_list[self.WIN_ID_CMD]
            # win.clear()
            # win.border()
            # win.addstr(0, 2, " COMMANDS ", A_BOLD)
            # cmd_str = "Add : INS/+, Del : DEL/-"
            # cmd_str = cmd_str + ", Open : ENTER"
            # cmd_str = cmd_str + ", Save : S, Ret : ESCAPE"
            # win.addstr(1, 2, cmd_str)
            # win.refresh()

            self.win_list[self.WIN_ID_SUB].keypad(True)
            key = self.win_list[self.WIN_ID_SUB].getkey()

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
                stat_hl.disp_mgr.browse(self.win_list)

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
