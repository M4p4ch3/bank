"""
display/curses/implem/statement
"""

import curses
from curses import A_BOLD
from datetime import datetime
from typing import (Any, List, Tuple)

from bank.display.my_curses.main import (ColorPairId, WinId, DisplayerMain)
from bank.display.my_curses.item_display import DisplayerItem
from bank.display.my_curses.container_display import DisplayerContainer
from bank.display.my_curses.implem.main import (FieldLen, formart_trunc_padd)
from bank.display.my_curses.implem.operation_display import DisplayerOperation

from bank.internal.statement import Statement
from bank.internal.operation import Operation

from bank.utils.my_date import FMT_DATE
from bank.utils.return_code import RetCode

class DisplayerStatement(DisplayerItem, DisplayerContainer):
    """
    Curses statement display
    """

    # Item separator
    SEPARATOR = "|"
    SEPARATOR += "-" + "-".ljust(FieldLen.LEN_DATE, "-") + "-|"
    SEPARATOR += "-" + "-".ljust(FieldLen.LEN_NAME, "-") + "-|"
    SEPARATOR += "-" + "-".ljust(FieldLen.LEN_AMOUNT, "-") + "-|"
    SEPARATOR += "-" + "-".ljust(FieldLen.LEN_AMOUNT, "-") + "-|"
    SEPARATOR += "-" + "-".ljust(FieldLen.LEN_AMOUNT, "-") + "-|"
    SEPARATOR += "-" + "-".ljust(FieldLen.LEN_AMOUNT, "-") + "-|"

    # Item header
    HEADER = "|"
    HEADER += " " + "date".ljust(FieldLen.LEN_DATE, " ") + " |"
    HEADER += " " + "name".ljust(FieldLen.LEN_NAME, " ") + " |"
    HEADER += " " + "start".ljust(FieldLen.LEN_AMOUNT, " ") + " |"
    HEADER += " " + "end".ljust(FieldLen.LEN_AMOUNT, " ") + " |"
    HEADER += " " + "diff".ljust(FieldLen.LEN_AMOUNT, " ") + " |"
    HEADER += " " + "error".ljust(FieldLen.LEN_AMOUNT, " ") + " |"

    # Item missing
    MISSING = "|"
    MISSING += " " + "...".ljust(FieldLen.LEN_DATE, " ") + " |"
    MISSING += " " + "...".ljust(FieldLen.LEN_NAME, " ") + " |"
    MISSING += " " + "...".ljust(FieldLen.LEN_AMOUNT, " ") + " |"
    MISSING += " " + "...".ljust(FieldLen.LEN_AMOUNT, " ") + " |"
    MISSING += " " + "...".ljust(FieldLen.LEN_AMOUNT, " ") + " |"

    def __init__(self, disp: DisplayerMain, stat: Statement = None) -> None:

        # Init self item display
        DisplayerItem.__init__(self, disp)

        # Init container item display
        ope_disp = DisplayerOperation(disp)

        # Init container display
        DisplayerContainer.__init__(self, disp, ope_disp)

        # self.item_disp: DisplayerOperation = DisplayerOperation(None, disp)

        # Statement
        self.stat: Statement = stat

        self.field_nb = Statement.FieldIdx.LAST + 1

        self.title = "STATEMENT"
        self.subtitle = "OPERATIONS LIST"

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
        elif field_idx == Statement.FieldIdx.NAME:
            ret = ("name", self.stat.name)
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
        elif field_idx == Statement.FieldIdx.NAME:
            self.stat.set_name(val_str)
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
            self.stat.file_sync = False

        return is_edited

    def get_container_item_list(self) -> List[Operation]:
        """
        Get statement operation list
        """

        return self.stat.ope_list

    def add_container_item(self, op: Operation) -> None:
        """
        Add statement operation
        """

        self.stat.add_ope(op)

    def remove_container_item_list(self, ope_list: List[Operation]) -> RetCode:
        """
        Remove statement operation list
        """

        ret = super().remove_container_item_list(ope_list)
        if ret == RetCode.CANCEL:
            return ret

        # Confirmed
        self.stat.remove_ope_list(ope_list)
        return RetCode.OK

    def remove_container_item(self, operation: Operation) -> None:
        """
        Remove statement operation

        Args:
            operation (Operation): operation
        """

        self.stat.remove_ope(operation)

    def edit_container_item(self, operation: Operation) -> None:
        """
        Edit operation

        Args:
            stat (Operation): Operation
        """

        # (Remove, edit, add) to update statment lsit and fields

        self.stat.remove_ope(operation)

        ope_disp = DisplayerOperation(self.disp, operation)
        ope_disp.edit_item()

        self.stat.add_ope(operation)

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
        ope_disp = DisplayerOperation(self.disp, operation)

        # Set operation fields
        ope_disp.edit_item(force_iterate=True)

        return operation

    def display_item_line(self, win: Any,
                          win_y: int, win_x: int, flag) -> None:
        """
        Display item line

        Args:
            win (Any): Window
            win_y (int): Y in window
            win_x (int): X in window
            flag ([type]): Display flag
        """

        stat_line = "| "
        stat_line += formart_trunc_padd(self.stat.date.strftime(FMT_DATE), FieldLen.LEN_DATE)
        stat_line += " | "
        stat_line += formart_trunc_padd(self.stat.name, FieldLen.LEN_NAME)
        stat_line += " | "
        stat_line += formart_trunc_padd(str(self.stat.bal_start), FieldLen.LEN_AMOUNT)
        stat_line += " | "
        stat_line += formart_trunc_padd(str(self.stat.bal_end), FieldLen.LEN_AMOUNT)
        stat_line += " | "

        win.addstr(win_y, win_x, stat_line, flag)

        bal_diff = round(self.stat.bal_end - self.stat.bal_start, 2)
        if bal_diff >= 0.0:
            win.addstr(str(bal_diff).ljust(FieldLen.LEN_AMOUNT),
                       curses.color_pair(ColorPairId.GREEN_BLACK) + flag)
        else:
            win.addstr(str(bal_diff).ljust(FieldLen.LEN_AMOUNT),
                       curses.color_pair(ColorPairId.RED_BLACK) + flag)

        win.addstr(" | ", flag)

        bal_err = round(self.stat.bal_start + self.stat.ope_sum - self.stat.bal_end, 2)
        if bal_err == 0.0:
            win.addstr(str(bal_err).ljust(FieldLen.LEN_AMOUNT),
                       curses.color_pair(ColorPairId.GREEN_BLACK) + flag)
        else:
            win.addstr(str(bal_err).ljust(FieldLen.LEN_AMOUNT),
                       curses.color_pair(ColorPairId.RED_BLACK) + flag)

        win.addstr(" |", flag)

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

        win.addstr(win_y, win_x, f"name : {self.stat.name}")
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
                   f"actual end : {(self.stat.bal_start + self.stat.ope_sum):.2f}")
        win_y += 1

        bal_err = round(self.stat.bal_start + self.stat.ope_sum - self.stat.bal_end, 2)
        win.addstr(win_y, win_x, "balance error : ")
        if bal_err == 0.0:
            win.addstr(str(bal_err), curses.color_pair(ColorPairId.GREEN_BLACK))
        else:
            win.addstr(str(bal_err), curses.color_pair(ColorPairId.RED_BLACK))
        win_y += 1

        win.addstr(win_y, win_x, "status : ")
        if self.stat.file_sync:
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

        self.stat.write_dir()

    def exit(self) -> RetCode:
        """
        Exit statement browse
        """

        # If saved
        if self.stat.file_sync:
            # Exit
            return RetCode.OK

        # Unsaved changes

        ret_super = super().exit()

        ret = RetCode.CANCEL
        if ret_super == RetCode.EXIT_SAVE:
            self.stat.write_dir()
            ret = RetCode.OK
        elif ret_super == RetCode.EXIT_NO_SAVE:
            ret = RetCode.OK

        return ret
