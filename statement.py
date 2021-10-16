
"""
Statement
"""

import csv
from datetime import datetime
import time
from typing import (TYPE_CHECKING, List, Tuple)

from utils import (OK, ERROR,
                   LEN_DATE, LEN_NAME, LEN_MODE, LEN_TIER, LEN_CAT, LEN_DESC, LEN_AMOUNT,
                   FMT_DATE)

from operation import Operation

try:
    from account import Account
except ImportError:
    # Fix cyclic import
    import sys
    Account = sys.modules["account"]

# Display
import curses
from curses import *

if TYPE_CHECKING:
    from _curses import _CursesWindow
    Window = _CursesWindow
else:
    from typing import Any
    Window = Any

class Statement():
    """
    Statement
    """

    # Field index
    IDX_INVALID = -1
    IDX_DATE = 0
    IDX_BAL_START = 1
    IDX_BAL_END = 2
    IDX_LAST = IDX_BAL_END

    def __init__(self, name: str, bal_start: float, bal_end: float, account: Account) -> None:

        self.name: str = name
        self.file_path: str = f"statements/{name}.csv"

        try:
            self.date: datetime = datetime.strptime(name, FMT_DATE)
        except ValueError:
            # For pending statement
            self.date: datetime = datetime.now()

        self.bal_start: float = bal_start
        self.bal_end: float = bal_end
        self.op_sum: float = 0.0
        self.op_list: List[Operation] = list()

        # Reference to account for operations buffer list
        self.account: Account = account

        # Display manager
        self.disp_mgr: StatementDispMgrCurses = StatementDispMgrCurses(self)

        self.is_unsaved: bool = False

    def get_str(self, indent: int = 0) -> str:
        """
        Get string representation
        """

        indent_str = ""
        for _ in range(indent):
            indent_str += "    "

        ret = ""
        ret += f"{indent_str}date : {self.date.strftime(FMT_DATE)}\n"
        ret += f"{indent_str}balance : [{str(self.bal_start)}, {str(self.bal_end)}]\n"
        ret += f"{indent_str}operations sum : {str(self.op_sum)}\n"
        ret += f"{indent_str}balance diff : {str(self.op_sum - self.bal_end)}\n"
        ret += f"{indent_str}operations : [\n"
        for op in self.op_list:
            ret += f"{indent_str}    {{\n"
            ret += op.get_str(indent + 2) + "\n"
            ret += f"{indent_str}    }}\n"
        ret += f"{indent_str}]"

        return ret

    def get_field(self, field_idx: int) -> Tuple[str, str]:
        """
        Get field (name, value), identified by field index
        Useful for iterating over fields
        """

        ret = ("", "")
        if field_idx == self.IDX_DATE:
            ret = ("date", self.date.strftime(FMT_DATE))
        elif field_idx == self.IDX_BAL_START:
            ret = ("start balance", str(self.bal_start))
        elif field_idx == self.IDX_BAL_END:
            ret = ("start balance", str(self.bal_end))

        return ret

    def get_closest_op(self, op_list: List[Operation]) -> Operation:
        """
        Get closest operation from list
        None if not found
        """

        # Operation to return
        op_ret: Operation = op_list[0]

        # While operation in list
        while (op_ret in op_list) and (op_ret is not None):

            # Get operation index in statement
            op_ret_idx = self.op_list.index(op_ret)

            # If first operation in list is first operation in statement
            if self.op_list.index(op_list[0]) == 0:
                # Search forward
                op_ret_idx = op_ret_idx + 1
            # Else, first operation in list is not first one
            else:
                # Search backward
                op_ret_idx = op_ret_idx - 1

            # If operation out of statement
            if op_ret_idx < 0 or op_ret_idx >= len(self.op_list):
                op_ret = None
            else:
                op_ret = self.op_list[op_ret_idx]

        return op_ret

    def set_field(self, field_idx, val_str) -> int:
        """
        Set field value, identified by field index, from string
        Useful for iterating over fields
        """

        if field_idx == self.IDX_DATE:
            try:
                self.date = datetime.strptime(val_str, FMT_DATE)
            except ValueError:
                return ERROR
        elif field_idx == self.IDX_BAL_START:
            try:
                self.bal_start = float(val_str)
            except ValueError:
                return ERROR
        elif field_idx == self.IDX_BAL_END:
            try:
                self.bal_end = float(val_str)
            except ValueError:
                return ERROR

        self.is_unsaved = True

        return OK

    def read(self) -> int:
        """
        Read from file
        """

        try:
            # Open CSV file
            file = open(self.file_path, "r")
            file_csv = csv.reader(file)
        except FileNotFoundError:
            # File not found
            # Create new statement
            file = open(self.file_path, "w+")
            file.close()
            # Don't proceed with read
            return OK

        # Clear operations list
        self.op_list.clear()
        # Reset operations sum
        self.op_sum = 0.0

        # For each operation line in statement CSV file
        for op_line in file_csv:

            # Create operation
            op_date = datetime.strptime(op_line[Operation.IDX_DATE], FMT_DATE)
            op = Operation(op_date, op_line[Operation.IDX_MODE], op_line[Operation.IDX_TIER],
                           op_line[Operation.IDX_CAT], op_line[Operation.IDX_DESC],
                           float(op_line[Operation.IDX_AMOUNT]))

            # Add operation to list
            self.op_list.append(op)

            # Update operations sum
            self.op_sum = self.op_sum + op.amount

        self.is_unsaved = False

        file.close()

        return OK

    def write(self) -> int:
        """
        Write CSV file
        """

        try:
            # Open CSV file
            file = open(self.file_path, "w")
        except FileNotFoundError:
            return ERROR

        file_csv = csv.writer(file, delimiter=',', quotechar='"')

        # For each operation
        for op in self.op_list:

            # TODO check if op has (date, op, tier, car desc, amount)

            # Create operation line
            op_csv = [op.date.strftime(FMT_DATE), op.mode, op.tier,
                      op.cat, op.desc, str(op.amount)]

            try:
                # Write operation line to CSV file
                file_csv.writerow(op_csv)
            # TODO add error type
            except:
                return ERROR

        self.is_unsaved = False

        file.close()

        return OK

    def reset(self) -> int:
        """
        Reset : Read
        """

        status: int = OK

        status = self.read()
        if status != OK:
            return ERROR

        return OK

    def save(self) -> int:
        """
        Save : Write
        """

        status: int = OK

        status = self.write()
        if status != OK:
            return ERROR

        return OK

    def insert_op(self, op: Operation) -> int:
        """
        Insert operation
        """

        # Find index
        idx = 0
        while idx < len(self.op_list) and op.date > self.op_list[idx].date:
            idx = idx + 1

        # Insert operation at dedicated index
        self.op_list.insert(idx, op)

        # Update operation sum
        self.op_sum += op.amount

        self.is_unsaved = True

        return OK

    def del_op_list(self, op_list: List[Operation]) -> None:
        """
        Delete operation list
        """

        # For each operation
        for op in op_list:
            # Remove operation from statement
            self.op_list.remove(op)
            # Update operation sum
            self.op_sum -= op.amount

        self.is_unsaved = True

class StatementDispMgrCurses():
    """
    Curses statetement display manager
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

    # Operation separator
    SEP_OP = "|"
    SEP_OP += "-" + "-".ljust(LEN_DATE, "-") + "-|"
    SEP_OP += "-" + "-".ljust(LEN_MODE, "-") + "-|"
    SEP_OP += "-" + "-".ljust(LEN_TIER, "-") + "-|"
    SEP_OP += "-" + "-".ljust(LEN_CAT, "-") + "-|"
    SEP_OP += "-" + "-".ljust(LEN_DESC, "-") + "-|"
    SEP_OP += "-" + "-".ljust(LEN_AMOUNT, "-") + "-|"

    # Operation missing
    MISS_OP = "|"
    MISS_OP += " " + "...".ljust(LEN_DATE, ' ') + " |"
    MISS_OP += " " + "...".ljust(LEN_MODE, ' ') + " |"
    MISS_OP += " " + "...".ljust(LEN_TIER, ' ') + " |"
    MISS_OP += " " + "...".ljust(LEN_CAT, ' ') + " |"
    MISS_OP += " " + "...".ljust(LEN_DESC, ' ') + " |"
    MISS_OP += " " + "...".ljust(LEN_AMOUNT, ' ') + " |"

    def __init__(self, stat: Statement) -> None:
        
        self.stat: Statement = stat

        # First displayed opeartion index
        self.op_disp_start_idx: int = 0

        # Last displayed opeartion index
        self.op_disp_last_idx: int = 0

        # Highlighted opeartion
        self.op_hl: Operation = None

        # Selected operations list
        self.op_sel_list: List[Operation] = []

    def display_op_list(self) -> None:

        # Set displayed operations number
        self.op_disp_nb = self.win_main_h - 11
        if len(self.stat.op_list) < self.op_disp_nb:
            self.op_disp_nb = len(self.stat.op_list)

        # Set last displayed operation index
        self.op_disp_last_idx = self.op_disp_start_idx + self.op_disp_nb - 1

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
        if self.op_disp_first_idx == 0:
            win.addstr(y, x, self.SEP_OP)
        else:
            win.addstr(y, x, self.MISS_OP)
        y = y + 1

        op_idx = self.op_disp_first_idx
        while op_idx < len(self.stat.op_list) and op_idx < self.op_disp_first_idx + self.op_disp_nb:

            op = self.stat.op_list[op_idx]

            disp_flag = A_NORMAL
            if op == self.op_hl:
                disp_flag += A_STANDOUT
            if op in self.op_sel_list:
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
        if op_idx == len(self.stat.op_list):
            win.addstr(y, x, self.SEP_OP)
        else:
            win.addstr(y, x, self.MISS_OP)
        y = y + 1

        if len(self.stat.op_list) != 0:
            # Slider
            # Move to top right of table
            (y, x) = (5, win.getyx()[1])
            for _ in range(int(self.op_disp_first_idx * self.op_disp_nb / len(self.stat.op_list))):
                win.addstr(y, x, " ")
                y = y + 1
            for _ in range(int(self.op_disp_nb * self.op_disp_nb / len(self.stat.op_list))):
                win.addstr(y, x, " ", A_STANDOUT)
                y = y + 1

        win.refresh()

    def display_fields(self) -> None:

        # Use info window
        win: Window = self.win_list[self.WIN_ID_INFO]

        win.clear()
        win.border()
        win.move(0, 2)
        win.addstr(" INFO ", A_BOLD)

        (y, x) = (2, 2)
        win.addstr(y, x, f"name : {self.stat.name}")
        y = y + 1
        win.addstr(y, x, f"date : {self.stat.date.strftime(FMT_DATE)}")
        y = y + 1
        win.addstr(y, x, f"start : {self.stat.bal_start}")
        y = y + 1
        win.addstr(y, x, f"end : {self.stat.bal_end}")
        y = y + 1
        win.addstr(y, x, f"actual end : {(self.stat.bal_start + self.stat.op_sum):.2f}")
        y = y + 1
        bal_diff = round(self.stat.bal_end - self.stat.bal_start, 2)
        win.addstr(y, x, f"diff : ")
        if bal_diff >= 0.0:
            win.addstr(str(bal_diff), curses.color_pair(self.COLOR_PAIR_ID_GREEN_BLACK))
        else:
            win.addstr(str(bal_diff), curses.color_pair(self.COLOR_PAIR_ID_RED_BLACK))
        y = y + 1
        bal_err = round(self.stat.bal_start + self.stat.op_sum - self.stat.bal_end, 2)
        win.addstr(y, x, f"err : ")
        if bal_err == 0.0:
            win.addstr(str(bal_err), curses.color_pair(self.COLOR_PAIR_ID_GREEN_BLACK))
        else:
            win.addstr(str(bal_err), curses.color_pair(self.COLOR_PAIR_ID_RED_BLACK))
        y = y + 1

        win.refresh()

    def browse(self, win_main: Window) -> None:

        # Get main window size
        (self.win_main_h, win_main_w) = win_main.getmaxyx()

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

        # Windows list
        self.win_list: List[Window] = [None] * (self.WIN_ID_LAST + 1)

        win_main.keypad(True)
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

        # Selected operations list
        self.op_sel_list: List[Operation] = []

        # First displayed operation
        self.op_disp_first_idx: int = 0

        # Highlighted operation
        self.op_hl: Operation = None
        if len(self.stat.op_list) != 0:
            self.op_hl = self.stat.op_list[0]

        while True:

            self.display_op_list()
            self.display_fields()

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
            if self.stat.is_unsaved:
                win.addstr(1, 2, "Unsaved", curses.color_pair(self.COLOR_PAIR_ID_RED_BLACK))
            else:
                win.addstr(1, 2, "Saved", curses.color_pair(self.COLOR_PAIR_ID_GREEN_BLACK))
            win.refresh()

            key = self.win_list[self.WIN_ID_MAIN].getkey()

            # Highlight previous operation
            if key == "KEY_UP":

                op_hl_idx = self.stat.op_list.index(self.op_hl) - 1
                if op_hl_idx < 0:
                    op_hl_idx = 0
                self.op_hl = self.stat.op_list[op_hl_idx]

                # If out of display range
                if op_hl_idx < self.op_disp_first_idx:
                    # Previous page
                    self.op_disp_first_idx = self.op_disp_first_idx - 1
                    if self.op_disp_first_idx < 0:
                        self.op_disp_first_idx = 0

            # Highlight next operation
            elif key == "KEY_DOWN":

                op_hl_idx = self.stat.op_list.index(self.op_hl) + 1
                if op_hl_idx >= len(self.stat.op_list):
                    op_hl_idx = len(self.stat.op_list) - 1
                self.op_hl = self.stat.op_list[op_hl_idx]

                # If out of display range
                if op_hl_idx > self.op_disp_last_idx:
                    # Next page
                    self.op_disp_first_idx = self.op_disp_first_idx + 1
                    if self.op_disp_first_idx > len(self.stat.op_list) - self.op_disp_nb:
                        self.op_disp_first_idx = len(self.stat.op_list) - self.op_disp_nb

            # Previous page
            elif key == "KEY_PPAGE":

                # Previous page
                self.op_disp_first_idx = self.op_disp_first_idx - 3
                if self.op_disp_first_idx < 0:
                    self.op_disp_first_idx = 0

                # If out of display range
                op_hl_idx = self.stat.op_list.index(self.op_hl)
                if op_hl_idx < self.op_disp_first_idx:
                    self.op_hl = self.stat.op_list[self.op_disp_first_idx]
                elif op_hl_idx >= self.op_disp_first_idx + self.op_disp_nb:
                    self.op_hl = self.stat.op_list[self.op_disp_first_idx + self.op_disp_nb - 1]

            # Next page
            elif key == "KEY_NPAGE":

                # Next page
                self.op_disp_first_idx = self.op_disp_first_idx + 3
                if self.op_disp_first_idx > len(self.stat.op_list) - self.op_disp_nb:
                    self.op_disp_first_idx = len(self.stat.op_list) - self.op_disp_nb
                    if self.op_disp_first_idx < 0:
                        self.op_disp_first_idx = 0

                # If out of display range
                op_hl_idx = self.stat.op_list.index(self.op_hl)
                if op_hl_idx < self.op_disp_first_idx:
                    self.op_hl = self.stat.op_list[self.op_disp_first_idx]
                elif op_hl_idx >= self.op_disp_first_idx + self.op_disp_nb:
                    self.op_hl = self.stat.op_list[self.op_disp_first_idx + self.op_disp_nb - 1]

            # (Un)select operation
            elif key == " ":
                # If operation not selected
                if self.op_hl not in self.op_sel_list:
                    # Add operation to selected ones
                    self.op_sel_list.append(self.op_hl)
                # Else, operation selected
                else:
                    # Remove operation from selected ones
                    self.op_sel_list.remove(self.op_hl)

            # Add operation
            elif key in ("KEY_IC", "+"):
                self.add_op()

            # Delete operation(s)
            elif key in ("KEY_DC", "-"):

                # If no selected operations
                if len(self.op_sel_list) == 0:
                    # Selected is highlighted operation
                    self.op_sel_list.append(self.op_hl)

                # Highlight closest operation
                self.op_hl = self.stat.get_closest_op(self.op_sel_list)

                # Delete selected operations from statement
                self.delete_op_list(self.op_sel_list)

                # Clear select operations
                self.op_sel_list.clear()

            # Copy operations(s)
            elif key == "c":

                if len(self.op_sel_list) == 0:
                    op_buffer_list = [self.op_hl]
                else:
                    op_buffer_list = self.op_sel_list

                self.stat.account.set_op_buffer(op_buffer_list)

            # Cut operation(s)
            elif key == "x":

                if len(self.op_sel_list) == 0:
                    op_buffer_list = [self.op_hl]
                else:
                    op_buffer_list = self.op_sel_list
                self.stat.account.set_op_buffer(op_buffer_list)

                if self.op_hl in op_buffer_list:
                    self.op_hl = self.stat.get_closest_op(op_buffer_list)

                self.stat.del_op_list(op_buffer_list)

            # Paste operation(s)
            elif key == "v":

                op_buffer_list = self.stat.account.get_op_buffer()

                for op in op_buffer_list:
                    # Deep copy
                    op_new = op.copy()
                    self.stat.insert_op(op_new)

            # Open highlighted operation
            elif key == "\n":

                (is_edited, is_date_edited) = self.op_hl.disp_mgr.browse(self.win_list[self.WIN_ID_INPUT])
                # If operation edited
                if is_edited:
                    self.stat.is_unsaved = True
                    # If date edited
                    if is_date_edited:
                        # Delete and insert opearion from/to statement
                        # To update index
                        self.stat.del_op_list([self.op_hl])
                        self.stat.insert_op(self.op_hl)

            # Save
            elif key == "s":
                self.stat.save()

            # Exit
            elif key == '\x1b':
                if self.stat.is_unsaved:
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
                        self.stat.save()
                    else:
                        win.addstr(4, 2, f"Discard changes",
                                   curses.color_pair(self.COLOR_PAIR_ID_RED_BLACK))
                        win.refresh()
                        time.sleep(1)
                        self.stat.reset()
                break

    def add_op(self) -> None:

        # Create empty opeartion
        op = Operation(datetime.now(), "", "", "", "", 0.0)

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

        self.stat.insert_op(op)

    def delete_op_list(self, op_list: List[Operation]) -> None:

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

        self.stat.del_op_list(op_list)
