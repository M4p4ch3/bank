
import curses
from curses import *
from datetime import datetime
from enum import IntEnum
import logging
from typing import (TYPE_CHECKING, Any, List, Union, Tuple)

from bank.display.my_curses.main import (NoOverrideError, ColorPairId, WinId, DispCurses)
from bank.display.my_curses.item_display import ItemDispCurses
from bank.display.my_curses.container_display import ContainerDispCurses
from bank.display.my_curses.implem.main import FieldLen
from bank.display.my_curses.implem.operation_display import OperationDispCurses

from bank.account import Account
from bank.statement import Statement
from bank.operation import Operation

from bank.utils.clipboard import Clipboard
from bank.utils.my_date import FMT_DATE
from bank.utils.return_code import RetCode

if TYPE_CHECKING:
    from _curses import _CursesWindow
    Window = _CursesWindow
else:
    from typing import Any
    Window = Any

class StatementDispCurses(ItemDispCurses, ContainerDispCurses):
    """
    Curses statement display
    """

    # Item separator
    SEPARATOR = "|"
    SEPARATOR += "-" + "-".ljust(FieldLen.LEN_NAME, "-") + "-|"
    SEPARATOR += "-" + "-".ljust(FieldLen.LEN_DATE, "-") + "-|"
    SEPARATOR += "-" + "-".ljust(FieldLen.LEN_AMOUNT, "-") + "-|"
    SEPARATOR += "-" + "-".ljust(FieldLen.LEN_AMOUNT, "-") + "-|"
    SEPARATOR += "-" + "-".ljust(FieldLen.LEN_AMOUNT, "-") + "-|"
    SEPARATOR += "-" + "-".ljust(FieldLen.LEN_AMOUNT, "-") + "-|"

    # Item header
    HEADER = "|"
    HEADER += " " + "name".ljust(FieldLen.LEN_DATE, " ") + " |"
    HEADER += " " + "date".ljust(FieldLen.LEN_DATE, " ") + " |"
    HEADER += " " + "start".ljust(FieldLen.LEN_AMOUNT, " ") + " |"
    HEADER += " " + "end".ljust(FieldLen.LEN_AMOUNT, " ") + " |"
    HEADER += " " + "diff".ljust(FieldLen.LEN_AMOUNT, " ") + " |"
    HEADER += " " + "error".ljust(FieldLen.LEN_AMOUNT, " ") + " |"

    # Item missing
    MISSING = "|"
    MISSING += " " + "...".ljust(FieldLen.LEN_NAME, " ") + " |"
    MISSING += " " + "...".ljust(FieldLen.LEN_DATE, " ") + " |"
    MISSING += " " + "...".ljust(FieldLen.LEN_AMOUNT, " ") + " |"
    MISSING += " " + "...".ljust(FieldLen.LEN_AMOUNT, " ") + " |"
    MISSING += " " + "...".ljust(FieldLen.LEN_AMOUNT, " ") + " |"

    def __init__(self, disp: DispCurses, stat: Statement = None) -> None:

        # Init self item display
        ItemDispCurses.__init__(self, disp)

        # Init container item display
        op_disp = OperationDispCurses(disp)

        # Init container display
        ContainerDispCurses.__init__(self, disp, op_disp)

        # self.item_disp: OperationDispCurses = OperationDispCurses(None, disp)

        # Statement
        self.stat: Statement = stat

        self.field_nb = Statement.FieldIdx.LAST + 1

        self.name = "STATEMENT"

    def set_item(self, stat: Statement) -> None:
        """
        Set statement
        """

        self.stat = stat

    def get_item_field(self, field_idx: int) -> Tuple[str, str]:
        """
        Get field (name, value), identified by field index
        """

        ret = ("", "")
        if field_idx == Statement.FieldIdx.DATE:
            ret = ("date", self.stat.date.strftime(FMT_DATE))
        elif field_idx == Statement.FieldIdx.BAL_START:
            ret = ("start balance", str(self.stat.bal_start))
        elif field_idx == Statement.FieldIdx.BAL_END:
            ret = ("end balance", str(self.stat.bal_end))

        return ret

    def set_item_field(self, field_idx: int, val_str: str) -> bool:
        """
        Set field value, identified by field index, from string
        """

        is_edited = True

        if field_idx == Statement.FieldIdx.DATE:
            try:
                self.stat.date = datetime.strptime(val_str, FMT_DATE)
            except ValueError:
                is_edited = False
        elif field_idx == Statement.FieldIdx.BAL_START:
            try:
                self.stat.bal_start = float(val_str)
            except ValueError:
                is_edited = False
        elif field_idx == Statement.FieldIdx.BAL_END:
            try:
                self.stat.bal_end = float(val_str)
            except ValueError:
                is_edited = False

        if is_edited:
            self.stat.is_saved = False

        return is_edited

    def get_container_item_list(self) -> List[Operation]:
        """
        Get statement operation list
        """

        return self.stat.op_list

    def add_container_item(self, op: Operation) -> None:
        """
        Add statement operation
        """

        self.stat.add_op(op)

    def remove_container_item_list(self, op_list: List[Operation]) -> RetCode:
        """
        Remove statement operation list
        """

        ret = super().remove_container_item_list(op_list)
        if ret == RetCode.CANCEL:
            return ret

        # Confirmed
        self.stat.remove_op_list(op_list)
        return RetCode.OK

    def edit_container_item(self, operation: Operation) -> None:
        """
        Edit operation

        Args:
            stat (Operation): Operation
        """

        op_disp = OperationDispCurses(self.disp, operation)
        is_edited = op_disp.edit_item()
        if is_edited:
            self.stat.is_saved = False

    def browse_container_item(self, operation: Operation) -> None:
        """
        Browse operation
        """

        self.edit_container_item(operation)

    def create_container_item(self) -> Operation:
        """
        Create statement operation
        """

        # Init operation
        operation: Operation = Operation(datetime.now(), "", "", "", "", 0.0)

        # Init operation display
        op_disp = OperationDispCurses(self.disp, operation)

        # Set operation fields
        op_disp.edit_item(force_iterate=True)

        return operation

    def display_item_line(self, win: Window,
                          win_y: int, win_x: int, flag) -> None:
        """
        Display item line

        Args:
            win (Window): Window
            win_y (int): Y in window
            win_x (int): X in window
            flag ([type]): Display flag
        """

        win.addstr(win_y, win_x, "| ")
        win.addstr(self.stat.date.strftime(FMT_DATE).ljust(FieldLen.LEN_NAME), flag)
        win.addstr(" | ")
        win.addstr(self.stat.date.strftime(FMT_DATE).ljust(FieldLen.LEN_DATE), flag)
        win.addstr(" | ")
        win.addstr(str(self.stat.bal_start).ljust(FieldLen.LEN_AMOUNT), flag)
        win.addstr(" | ")
        win.addstr(str(self.stat.bal_end).ljust(FieldLen.LEN_AMOUNT), flag)
        win.addstr(" | ")
        bal_diff = round(self.stat.bal_end - self.stat.bal_start, 2)
        if bal_diff >= 0.0:
            win.addstr(str(bal_diff).ljust(FieldLen.LEN_AMOUNT),
                       curses.color_pair(ColorPairId.GREEN_BLACK))
        else:
            win.addstr(str(bal_diff).ljust(FieldLen.LEN_AMOUNT),
                       curses.color_pair(ColorPairId.RED_BLACK))
        win.addstr(" | ")
        bal_err = round(self.stat.bal_start + self.stat.op_sum - self.stat.bal_end, 2)
        if bal_err == 0.0:
            win.addstr(str(bal_err).ljust(FieldLen.LEN_AMOUNT),
                       curses.color_pair(ColorPairId.GREEN_BLACK))
        else:
            win.addstr(str(bal_err).ljust(FieldLen.LEN_AMOUNT),
                       curses.color_pair(ColorPairId.RED_BLACK))
        win.addstr(" |")

    def display_container_info(self) -> None:
        """
        Display statement info
        """

        # Top right window
        win = self.disp.win_list[WinId.RIGHT_TOP]

        win.clear()
        win.border()
        win.addstr(0, 2, " INFO ", A_BOLD)

        (win_y, win_x) = (2, 2)
        win.addstr(win_y, win_x, f"date : {self.stat.date.strftime(FMT_DATE)}")
        win_y += 1

        win.addstr(win_y, win_x, f"balance start : {self.stat.bal_start}")
        win_y += 1

        win.addstr(win_y, win_x, f"balance end : {self.stat.bal_end}")
        win_y += 1

        bal_diff = round(self.stat.bal_end - self.stat.bal_start, 2)
        win.addstr(win_y, win_x, "balance diff : ")
        if bal_diff >= 0.0:
            win.addstr(str(bal_diff), curses.color_pair(ColorPairId.GREEN_BLACK))
        else:
            win.addstr(str(bal_diff), curses.color_pair(ColorPairId.RED_BLACK))
        win_y += 1

        win.addstr(win_y, win_x,
                   f"actual end : {(self.stat.bal_start + self.stat.op_sum):.2f}")
        win_y += 1

        bal_err = round(self.stat.bal_start + self.stat.op_sum - self.stat.bal_end, 2)
        win.addstr(win_y, win_x, "balance error : ")
        if bal_err == 0.0:
            win.addstr(str(bal_err), curses.color_pair(ColorPairId.GREEN_BLACK))
        else:
            win.addstr(str(bal_err), curses.color_pair(ColorPairId.RED_BLACK))
        win_y += 1

        win.addstr(win_y, win_x, "status : ")
        if self.stat.is_saved:
            win.addstr("Saved", curses.color_pair(ColorPairId.GREEN_BLACK))
        else:
            win.addstr("Unsaved", curses.color_pair(ColorPairId.RED_BLACK))
        win_y += 1

        win.addstr(win_y, win_x,
                   f"clipboard : {self.disp.item_list_clipboard.get_len()} operations")
        win_y += 1

        win.refresh()

    def save(self) -> None:
        """
        Stave statement
        """

        self.stat.export_file()

    def exit(self) -> RetCode:
        """
        Exit statement browse
        """

        # If saved
        if self.stat.is_saved:
            # Exit
            return RetCode.OK

        # Unsaved changes

        ret_super = super().exit()

        ret = RetCode.CANCEL
        if ret_super == RetCode.EXIT_SAVE:
            self.stat.export_file()
            ret = RetCode.OK
        elif ret_super == RetCode.EXIT_NO_SAVE:
            ret = RetCode.OK

        return ret