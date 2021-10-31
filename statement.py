"""
Statement
"""

import csv
from datetime import datetime
from typing import (TYPE_CHECKING, List, Tuple)

from operation import Operation, OperationDispMgrCurses
from utils import (LEN_DATE, LEN_MODE, LEN_TIER, LEN_CAT, LEN_DESC, LEN_AMOUNT,
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

class Statement():
    """
    Statement
    """

    # Field index
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

        # Import from file
        self.import_file()

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

    def import_file(self) -> None:
        """
        Import operations from file
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
            # Don't proceed with import
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

    def export_file(self) -> None:
        """
        Export operations to file
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

    def __init__(self, stat: Statement, win_list: List[Window],
                 op_list_clipboard: Clipboard) -> None:

        # Statement
        self.stat: Statement = stat

        # Windows list
        self.win_list: List[Window] = win_list

        # Operations list clipboard
        self.op_list_clipboard: Clipboard = op_list_clipboard

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

        # Main window
        win_main: Window = self.win_list[WinId.MAIN]
        win_main.clear()
        win_main.border()
        win_main.move(0, 2)
        win_main.addstr(" STATEMENT ", A_BOLD)
        win_main.refresh()

        # Sub main window
        win_sub: Window = self.win_list[WinId.SUB]
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
            op_str += " " + operation.date.strftime(FMT_DATE).ljust(LEN_DATE, ' ') + " |"
            op_str += " " + operation.mode.ljust(LEN_MODE, ' ') + " |"
            op_str += " " + operation.tier.ljust(LEN_TIER, ' ') + " |"
            op_str += " " + operation.cat.ljust(LEN_CAT, ' ') + " |"
            op_str += " " + operation.desc.ljust(LEN_DESC, ' ') + " |"
            op_str += " " + str(operation.amount).ljust(LEN_AMOUNT, ' ') + " |"
            win_sub.addstr(win_y, win_x, op_str, disp_flag)
            win_y += 1

        # Operation separator or missing
        if op_idx == len(self.stat.op_list) - 1:
            win_sub.addstr(win_y, win_x, self.OP_SEP)
        else:
            win_sub.addstr(win_y, win_x, self.OP_MISS)
        win_y += 1

        # Slider
        if len(self.stat.op_list) != 0:
            (win_y, win_x) = (3, win_sub.getyx()[1])
            win_y += int(self.op_focus_idx * op_disp_nb / len(self.stat.op_list))
            for _ in range(int(op_disp_nb * op_disp_nb / len(self.stat.op_list))):
                win_sub.addstr(win_y, win_x, " ", A_STANDOUT)
                win_y += 1

        win_sub.refresh()

    def display_info(self) -> None:
        """
        Display statement info
        """

        # Info window
        win_info: Window = self.win_list[WinId.INFO]

        win_info.clear()
        win_info.border()
        win_info.addstr(0, 2, " INFO ", A_BOLD)

        (win_y, win_x) = (2, 2)
        win_info.addstr(win_y, win_x, f"name : {self.stat.name}")
        win_y += 1

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

        win_info.addstr(win_y, win_x, f"clipboard : {self.op_list_clipboard.get_len()} operations")
        win_y += 1

        win_info.refresh()

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

    def copy_op_list(self) -> None:
        """
        Copy selected operations

        Set clipboard to selected operations
        """

        if len(self.op_sel_list) > 0:
            op_list = self.op_sel_list
        else:
            op_list = [self.op_hl]

        self.op_list_clipboard.set(op_list)

    def cut_op_list(self) -> None:
        """
        Cut selected operations

        Set clipboard to selected operations
        Delete from statement
        """

        if len(self.op_sel_list) > 0:
            op_list = self.op_sel_list
        else:
            op_list = [self.op_hl]

        self.op_list_clipboard.set(op_list)

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

        op_list = self.op_list_clipboard.get()
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

        is_hl_updated = False
        is_focus_updated = False

        while True:

            # Display operations list
            self.display_op_list(is_hl_updated, is_focus_updated)

            # Display updated
            is_hl_updated = False
            is_focus_updated = False

            # Display statement info
            self.display_info()

            # Display commands
            # self.display_commands()

            key = self.win_list[WinId.MAIN].getkey()

            # Highlight previous operation
            if key == "KEY_UP":
                op_hl_idx = self.stat.op_list.index(self.op_hl) - 1
                if op_hl_idx < 0:
                    op_hl_idx = 0
                    continue
                self.op_hl = self.stat.op_list[op_hl_idx]
                is_hl_updated = True

            # Highlight next operation
            elif key == "KEY_DOWN":
                op_hl_idx = self.stat.op_list.index(self.op_hl) + 1
                if op_hl_idx >= len(self.stat.op_list):
                    op_hl_idx = len(self.stat.op_list) - 1
                    continue
                self.op_hl = self.stat.op_list[op_hl_idx]
                is_hl_updated = True

            # Focus previous operations
            elif key == "KEY_PPAGE":
                self.op_focus_idx -= 3
                is_focus_updated = True

            # Focus next operations
            elif key == "KEY_NPAGE":
                self.op_focus_idx += 3
                is_focus_updated = True

            # Trigger operation selection
            elif key == " ":
                if self.op_hl not in self.op_sel_list:
                    self.op_sel_list.append(self.op_hl)
                else:
                    self.op_sel_list.remove(self.op_hl)

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
                self.stat.export_file()

            # Exit
            elif key == '\x1b':
                self.exit()
                break
