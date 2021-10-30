"""
Statement
"""

import csv
from datetime import datetime
from typing import (TYPE_CHECKING, List, Tuple)

from operation import Operation, OperationDispMgrCurses
from utils import (LEN_DATE, LEN_MODE, LEN_TIER, LEN_CAT, LEN_DESC, LEN_AMOUNT,
                   FMT_DATE,
                   WinId, ColorPairId, ObjListBuffer)

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

    def __init__(self, name: str, bal_start: float, bal_end: float) -> None:

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
        for operation in self.op_list:
            ret += f"{indent_str}    {{\n"
            ret += operation.get_str(indent + 2) + "\n"
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

    def set_field(self, field_idx, val_str) -> bool:
        """
        Set field value, identified by field index, from string
        Useful for iterating over fields
        """

        is_edited = True

        if field_idx == self.IDX_DATE:
            try:
                self.date = datetime.strptime(val_str, FMT_DATE)
            except ValueError:
                is_edited = False
        elif field_idx == self.IDX_BAL_START:
            try:
                self.bal_start = float(val_str)
            except ValueError:
                is_edited = False
        elif field_idx == self.IDX_BAL_END:
            try:
                self.bal_end = float(val_str)
            except ValueError:
                is_edited = False

        if is_edited:
            self.is_unsaved = True

        return is_edited

    def read(self) -> None:
        """
        Read from file
        """

        try:
            # Open CSV file
            file = open(self.file_path, "r", encoding="utf8")
            file_csv = csv.reader(file)
        except FileNotFoundError:
            # File not found
            # Create new statement
            file = open(self.file_path, "w+", encoding="utf8")
            file.close()
            # Don't proceed with read
            return

        # Clear operations list
        self.op_list.clear()
        # Reset operations sum
        self.op_sum = 0.0

        # For each operation line in statement CSV file
        for op_line in file_csv:

            # Create operation
            op_date = datetime.strptime(op_line[Operation.IDX_DATE], FMT_DATE)
            operation = Operation(op_date, op_line[Operation.IDX_MODE], op_line[Operation.IDX_TIER],
                           op_line[Operation.IDX_CAT], op_line[Operation.IDX_DESC],
                           float(op_line[Operation.IDX_AMOUNT]))

            # Add operation to list
            self.op_list.append(operation)

            # Update operations sum
            self.op_sum = self.op_sum + operation.amount

        self.is_unsaved = False

        file.close()

    def write(self) -> None:
        """
        Write CSV file
        """

        # Open CSV file
        file = open(self.file_path, "w", encoding="utf8")

        file_csv = csv.writer(file, delimiter=',', quotechar='"')

        # For each operation
        for operation in self.op_list:

            # Create operation line
            op_csv = [operation.date.strftime(FMT_DATE), operation.mode, operation.tier,
                      operation.cat, operation.desc, str(operation.amount)]

            # Write operation line to CSV file
            file_csv.writerow(op_csv)

        self.is_unsaved = False

        file.close()

    def reset(self):
        """
        Reset : Read
        """

        self.read()

    def save(self):
        """
        Save : Write
        """

        self.write()

    def insert_op(self, operation: Operation) -> None:
        """
        Insert operation
        """

        # Find index
        idx = 0
        while idx < len(self.op_list) and operation.date > self.op_list[idx].date:
            idx = idx + 1

        # Insert operation at dedicated index
        self.op_list.insert(idx, operation)

        # Update operation sum
        self.op_sum += operation.amount

        self.is_unsaved = True

    def del_op_list(self, op_list: List[Operation]) -> None:
        """
        Delete operation list
        """

        # For each operation
        for operation in op_list:
            # Remove operation from statement
            self.op_list.remove(operation)
            # Update operation sum
            self.op_sum -= operation.amount

        self.is_unsaved = True

class StatementDispMgrCurses():
    """
    Curses statetement display manager
    """

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

    def __init__(self, stat: Statement, win_list: List[Window],
                 op_list_buffer: ObjListBuffer) -> None:

        # Statement
        self.stat: Statement = stat

        # Windows list
        self.win_list: List[Window] = win_list

        # Operations list buffer
        self.op_list_buffer: ObjListBuffer = op_list_buffer

        # Index of first displayed operation
        self.op_disp_first_idx: int = 0

        # Highlighted operation
        self.op_hl: Operation = None

        # Selected operations list
        self.op_sel_list: List[Operation] = []

        win_sub_h = self.win_list[WinId.SUB].getmaxyx()[0]

        # Number of displayed operations
        self.op_disp_nb: int = win_sub_h - 4

    def display_op_list(self) -> None:
        """
        Display operations list
        """

        # Set displayed operations number
        win_sub_h = self.win_list[WinId.SUB].getmaxyx()[0]
        self.op_disp_nb: int = win_sub_h - 4
        if len(self.stat.op_list) < self.op_disp_nb:
            self.op_disp_nb = len(self.stat.op_list)

        # Main window
        win: Window = self.win_list[WinId.MAIN]

        # Border
        win.clear()
        win.border()
        win.move(0, 2)
        win.addstr(" STATEMENT ", A_BOLD)

        # Status
        win_main_w = self.win_list[WinId.MAIN].getmaxyx()[1]
        if self.stat.is_unsaved:
            win.addstr(0, win_main_w - 10, "Unsaved", curses.color_pair(ColorPairId.RED_BLACK))
        else:
            win.addstr(0, win_main_w - 10, "Saved", curses.color_pair(ColorPairId.GREEN_BLACK))

        # Refresh
        win.refresh()

        # Use sub main window
        win: Window = self.win_list[WinId.SUB]

        (win_y, win_x) = (0, 0)
        win.addstr(win_y, win_x, self.SEP_OP)
        win_y = win_y + 1

        win.addstr(win_y, win_x, "| ")
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
        win_y = win_y + 1

        # Operation separator or missing
        if self.op_disp_first_idx == 0:
            win.addstr(win_y, win_x, self.SEP_OP)
        else:
            win.addstr(win_y, win_x, self.MISS_OP)
        win_y = win_y + 1

        op_idx = self.op_disp_first_idx
        while op_idx < len(self.stat.op_list) and op_idx < self.op_disp_first_idx + self.op_disp_nb:

            operation = self.stat.op_list[op_idx]

            disp_flag = A_NORMAL
            if operation == self.op_hl:
                disp_flag += A_STANDOUT
            if operation in self.op_sel_list:
                disp_flag += A_BOLD

            win.addstr(win_y, win_x, "| ")
            win.addnstr(operation.date.strftime(FMT_DATE).ljust(LEN_DATE), LEN_DATE, disp_flag)
            win.addstr(" | ")
            win.addnstr(operation.mode.ljust(LEN_MODE), LEN_MODE, disp_flag)
            win.addstr(" | ")
            win.addnstr(operation.tier.ljust(LEN_TIER), LEN_TIER, disp_flag)
            win.addstr(" | ")
            win.addnstr(operation.cat.ljust(LEN_CAT), LEN_CAT, disp_flag)
            win.addstr(" | ")
            win.addnstr(operation.desc.ljust(LEN_DESC), LEN_DESC, disp_flag)
            win.addstr(" | ")
            win.addnstr(str(operation.amount).ljust(LEN_AMOUNT), LEN_AMOUNT, disp_flag)
            win.addstr(" |")
            win_y = win_y + 1

            op_idx = op_idx + 1

        # Operation separator or missing
        if op_idx == len(self.stat.op_list):
            win.addstr(win_y, win_x, self.SEP_OP)
        else:
            win.addstr(win_y, win_x, self.MISS_OP)
        win_y = win_y + 1

        if len(self.stat.op_list) != 0:
            # Slider
            # Move to top right of table
            (win_y, win_x) = (3, win.getyx()[1])
            for _ in range(int(self.op_disp_first_idx * self.op_disp_nb / len(self.stat.op_list))):
                win.addstr(win_y, win_x, " ")
                win_y = win_y + 1
            for _ in range(int(self.op_disp_nb * self.op_disp_nb / len(self.stat.op_list))):
                win.addstr(win_y, win_x, " ", A_STANDOUT)
                win_y = win_y + 1

        win.refresh()

    def display_fields(self) -> None:
        """
        Display statement fields
        """

        # Use info window
        win: Window = self.win_list[WinId.INFO]

        win.clear()
        win.border()
        win.move(0, 2)
        win.addstr(" INFO ", A_BOLD)

        (win_y, win_x) = (2, 2)
        win.addstr(win_y, win_x, f"name : {self.stat.name}")
        win_y = win_y + 1
        win.addstr(win_y, win_x, f"date : {self.stat.date.strftime(FMT_DATE)}")
        win_y = win_y + 1
        win.addstr(win_y, win_x, f"start : {self.stat.bal_start}")
        win_y = win_y + 1
        win.addstr(win_y, win_x, f"end : {self.stat.bal_end}")
        win_y = win_y + 1
        win.addstr(win_y, win_x, f"actual end : {(self.stat.bal_start + self.stat.op_sum):.2f}")
        win_y = win_y + 1
        bal_diff = round(self.stat.bal_end - self.stat.bal_start, 2)
        win.addstr(win_y, win_x, "diff : ")
        if bal_diff >= 0.0:
            win.addstr(str(bal_diff), curses.color_pair(ColorPairId.GREEN_BLACK))
        else:
            win.addstr(str(bal_diff), curses.color_pair(ColorPairId.RED_BLACK))
        win_y = win_y + 1
        bal_err = round(self.stat.bal_start + self.stat.op_sum - self.stat.bal_end, 2)
        win.addstr(win_y, win_x, "err : ")
        if bal_err == 0.0:
            win.addstr(str(bal_err), curses.color_pair(ColorPairId.GREEN_BLACK))
        else:
            win.addstr(str(bal_err), curses.color_pair(ColorPairId.RED_BLACK))
        win_y = win_y + 1

        win.refresh()

    # def display_commands(self) -> None:

    #     win: Window = self.win_list[WinId.CMD]
    #     win.clear()
    #     win.border()
    #     win.addstr(0, 2, " COMMANDS ", A_BOLD)
    #     cmd_str = "Add : INS/+, Del : DEL/-"
    #     cmd_str = cmd_str + ", Dupl : D, (Un)sel : SPACE, Move : M "
    #     cmd_str = cmd_str + ", Open : ENTER"
    #     cmd_str = cmd_str + ", Save : S, Ret : ESCAPE"
    #     win.addstr(1, 2, cmd_str)
    #     win.refresh()

    # def display_status(self) -> None:

    #     win: Window = self.win_list[WinId.STATUS]
    #     win.clear()
    #     win.border()
    #     win.addstr(0, 2, " STATUS ", A_BOLD)
    #     if self.stat.is_unsaved:
    #         win.addstr(1, 2, "Unsaved", curses.color_pair(ColorPairId.RED_BLACK))
    #     else:
    #         win.addstr(1, 2, "Saved", curses.color_pair(ColorPairId.GREEN_BLACK))
    #     win.refresh()

    def hl_prev_op(self) -> None:
        """
        Highlight previous operation
        """

        # Get highlighted operation index
        op_hl_idx = self.stat.op_list.index(self.op_hl)

        # Highlight previous operation
        op_hl_idx -= 1
        if op_hl_idx < 0:
            op_hl_idx = 0

        # Update highlighted operation
        self.op_hl = self.stat.op_list[op_hl_idx]

        # If highlighted operation out of display
        if op_hl_idx < self.op_disp_first_idx:

            # Move focus up
            self.op_disp_first_idx -= 1
            if self.op_disp_first_idx < 0:
                self.op_disp_first_idx = 0

    def hl_next_op(self) -> None:
        """
        Highlight next operation
        """

        # Get highlighted operation index
        op_hl_idx = self.stat.op_list.index(self.op_hl)

        # Highlight next operation
        op_hl_idx += 1
        if op_hl_idx >= len(self.stat.op_list):
            op_hl_idx = len(self.stat.op_list) - 1

        # Update highlighted operation
        self.op_hl = self.stat.op_list[op_hl_idx]

        # If highlighted operation out of display
        if op_hl_idx > self.op_disp_first_idx + self.op_disp_nb - 1:

            # Move focus down
            self.op_disp_first_idx += 1
            if self.op_disp_first_idx > len(self.stat.op_list) - self.op_disp_nb:
                self.op_disp_first_idx = len(self.stat.op_list) - self.op_disp_nb

    def move_prev_page(self) -> None:
        """"
        Move view to previous page
        """

        # Move display to previous page
        self.op_disp_first_idx -= 3
        if self.op_disp_first_idx < 0:
            self.op_disp_first_idx = 0

        # Get highlighted operation index
        op_hl_idx = self.stat.op_list.index(self.op_hl)

        # If highlighted operation out of display
        if op_hl_idx > self.op_disp_first_idx + self.op_disp_nb - 1:

            # Highlight last displayed information
            op_hl_idx = self.op_disp_first_idx + self.op_disp_nb - 1

            # Update highlighted operation
            self.op_hl = self.stat.op_list[op_hl_idx]

    def move_next_page(self) -> None:
        """
        Move view to next page
        """

        # Move display to next page
        self.op_disp_first_idx += 3
        if self.op_disp_first_idx > len(self.stat.op_list) - self.op_disp_nb:
            self.op_disp_first_idx = len(self.stat.op_list) - self.op_disp_nb

        # Get highlighted operation index
        op_hl_idx = self.stat.op_list.index(self.op_hl)

        # If highlighted operation out of display
        if op_hl_idx < self.op_disp_first_idx:

            # Highlight first displayed information
            op_hl_idx = self.op_disp_first_idx

            # Update highlighted operation
            self.op_hl = self.stat.op_list[op_hl_idx]

    def trigger_op_sel(self) -> None:
        """
        Trigger highlighted operation selection
        """

        # If highlighted operation not selected
        if self.op_hl not in self.op_sel_list:
            # Select operation
            self.op_sel_list.append(self.op_hl)
        # Else, highlighted operation selected
        else:
            # Unseleect highlighted operation
            self.op_sel_list.remove(self.op_hl)

    def copy_op_list(self) -> None:
        """
        Copy highlighted operation or selected operations list to buffer
        """

        # Account operations buffer list : Selected operations
        op_list = self.op_sel_list
        # If no selected opearations
        if len(op_list) == 0:
            # Account operations buffer list : Highlighted one
            op_list = [self.op_hl]

        # Set account operations buffer list
        self.op_list_buffer.set(op_list)

    def cut_op_list(self) -> None:
        """
        Cut highlighted operation or selected operations list to buffer
        """

        # Account operations buffer list : Selected operations
        op_list = self.op_sel_list
        # If no selected opearations
        if len(op_list) == 0:
            # Account operations buffer list : Highlighted one
            op_list = [self.op_hl]

        # Set account operations buffer list
        self.op_list_buffer.set(op_list)

        # If highlighted operation in buffer
        if self.op_hl in op_list:
            # Highlight closest opeartion
            self.op_hl = self.stat.get_closest_op(op_list)

        # Delete operations in buffer from statement
        self.stat.del_op_list(op_list)

    def paste_op_list(self) -> None:
        """
        Paste operations list from buffer
        """

        # Get account operations buffer list
        op_list = self.op_list_buffer.get()
        if op_list is None or len(op_list) == 0:
            return

        # For each operation i buffer
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
        op_disp_mgr: OperationDispMgrCurses = OperationDispMgrCurses(
            self.op_hl, self.win_list[WinId.INPUT])
        (is_edited, is_date_edited) = op_disp_mgr.browse()

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

        # Set operation fields using display manager
        op_disp_mgr: OperationDispMgrCurses = OperationDispMgrCurses(operation,
            self.win_list[WinId.INPUT])
        op_disp_mgr.set_fields()

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
        win = self.win_list[WinId.INPUT]
        win.clear()
        win.border()
        win.addstr(0, 2, " DELETE OPERATIONS ", A_BOLD)
        win.addstr(2, 2, f"Delete {len(op_del_list)} operations")
        win.addstr(4, 2, "Confirm ? (y/n) : ")
        confirm_c = win.getch()
        if confirm_c != ord('win_y'):
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
            win: Window = self.win_list[WinId.INPUT]
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
                self.stat.save()

            # Else, 'n'
            else:

                # Discard changes
                win.addstr(4, 2, "Discard changes",
                            curses.color_pair(ColorPairId.RED_BLACK))
                win.refresh()
                self.stat.reset()

    def browse(self) -> None:
        """
        Browse
        """

        # First displayed operation
        self.op_disp_first_idx: int = 0

        # Highlighted operation
        self.op_hl: Operation = None
        if len(self.stat.op_list) != 0:
            self.op_hl = self.stat.op_list[0]

        # Selected operations list
        self.op_sel_list: List[Operation] = []

        while True:

            # Displays operations list
            self.display_op_list()

            # Display statements fields
            self.display_fields()

            # Display commands
            # self.display_commands()

            # Display status
            # self.display_status()

            key = self.win_list[WinId.MAIN].getkey()

            # Highlight previous operation
            if key == "KEY_UP":
                self.hl_prev_op()
            # Highlight next operation
            elif key == "KEY_DOWN":
                self.hl_next_op()
            # Move to previous page
            elif key == "KEY_PPAGE":
                self.move_prev_page()
            # Next page
            elif key == "KEY_NPAGE":
                self.move_next_page()
            # (Un)select operation
            elif key == " ":
                self.trigger_op_sel()
            # Copy operations(s)
            elif key == "c":
                self.copy_op_list()
            # Cut operation(s)
            elif key == "x":
                self.cut_op_list()
            # Paste operation(s)
            elif key == "v":
                self.paste_op_list()
            # Open highlighted operation
            elif key == "\n":
                self.browse_op()
            # Add operation
            elif key in ("KEY_IC", "+"):
                self.add_op()
            # Delete operation(s)
            elif key in ("KEY_DC", "-"):
                self.delete_op()
            # Save
            elif key == "s":
                self.stat.save()
            # Exit
            elif key == '\x1b':
                self.exit()
                break
