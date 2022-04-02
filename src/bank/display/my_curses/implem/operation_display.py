"""
display/curses/implem/operation
"""

# import curses
from datetime import datetime
from typing import (Any, Tuple)

from bank.display.my_curses.main import (WinId, DisplayerMain)
from bank.display.my_curses.item_display import DisplayerItem
from bank.display.my_curses.implem.main import (FieldLen, formart_trunc_padd)

from bank.internal.operation import Operation

from bank.utils.my_date import FMT_DATE

class DisplayerOperation(DisplayerItem):
    """
    Curses operation display
    """

    # Item separator
    SEPARATOR = "|"
    SEPARATOR += "-" + "-".ljust(FieldLen.LEN_DATE, "-") + "-|"
    SEPARATOR += "-" + "-".ljust(FieldLen.LEN_MODE, "-") + "-|"
    SEPARATOR += "-" + "-".ljust(FieldLen.LEN_TIER, "-") + "-|"
    SEPARATOR += "-" + "-".ljust(FieldLen.LEN_CAT, "-") + "-|"
    SEPARATOR += "-" + "-".ljust(FieldLen.LEN_DESC, "-") + "-|"
    SEPARATOR += "-" + "-".ljust(FieldLen.LEN_AMOUNT, "-") + "-|"

    # Item header
    HEADER = "|"
    HEADER += " " + "date".ljust(FieldLen.LEN_DATE, " ") + " |"
    HEADER += " " + "mode".ljust(FieldLen.LEN_MODE, " ") + " |"
    HEADER += " " + "tier".ljust(FieldLen.LEN_TIER, " ") + " |"
    HEADER += " " + "cat".ljust(FieldLen.LEN_CAT, " ") + " |"
    HEADER += " " + "desc".ljust(FieldLen.LEN_DESC, " ") + " |"
    HEADER += " " + "amount".ljust(FieldLen.LEN_AMOUNT, " ") + " |"

    # Item missing
    MISSING = "|"
    MISSING += " " + "...".ljust(FieldLen.LEN_DATE, ' ') + " |"
    MISSING += " " + "...".ljust(FieldLen.LEN_MODE, ' ') + " |"
    MISSING += " " + "...".ljust(FieldLen.LEN_TIER, ' ') + " |"
    MISSING += " " + "...".ljust(FieldLen.LEN_CAT, ' ') + " |"
    MISSING += " " + "...".ljust(FieldLen.LEN_DESC, ' ') + " |"
    MISSING += " " + "...".ljust(FieldLen.LEN_AMOUNT, ' ') + " |"

    def __init__(self, disp: DisplayerMain, operation: Operation = None) -> None:

        # Init item display
        DisplayerItem.__init__(self, disp)

        # Operation
        self.operation: Operation = operation

        # Window
        self.win = disp.win_list[WinId.RIGHT_BOT]

        # Index of operation highlighted field
        self.ope_field_hl_idx = 0

        self.field_nb = Operation.FieldIdx.LAST + 1

        self.name = "OPERATION"

    def set_item(self, operation: Operation):
        """
        Set operation
        """

        self.operation = operation

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

        ope_line = "| "
        ope_line += formart_trunc_padd(self.operation.date.strftime(FMT_DATE), FieldLen.LEN_DATE)
        ope_line += " | "
        ope_line += formart_trunc_padd(self.operation.mode, FieldLen.LEN_MODE)
        ope_line += " | "
        ope_line += formart_trunc_padd(self.operation.tier, FieldLen.LEN_TIER)
        ope_line += " | "
        ope_line += formart_trunc_padd(self.operation.cat, FieldLen.LEN_CAT)
        ope_line += " | "
        ope_line += formart_trunc_padd(self.operation.desc, FieldLen.LEN_DESC)
        ope_line += " | "
        ope_line += formart_trunc_padd(str(self.operation.amount), FieldLen.LEN_AMOUNT)
        ope_line += " |"

        win.addstr(win_y, win_x, ope_line, flag)

    def get_item_field(self, field_idx) -> Tuple[str, str]:
        """
        Get field (name, value), identified by field index
        Useful for iterating over fields
        """

        ret = ("", "")

        if field_idx == Operation.FieldIdx.DATE:
            ret = ("date", self.operation.date.strftime(FMT_DATE))
        elif field_idx == Operation.FieldIdx.MODE:
            ret = ("mode", self.operation.mode)
        elif field_idx == Operation.FieldIdx.TIER:
            ret = ("tier", self.operation.tier)
        elif field_idx == Operation.FieldIdx.CAT:
            ret = ("cat", self.operation.cat)
        elif field_idx == Operation.FieldIdx.DESC:
            ret = ("desc", self.operation.desc)
        elif field_idx == Operation.FieldIdx.AMOUNT:
            ret = ("amount", str(self.operation.amount))

        return ret

    def set_item_field(self, field_idx, val_str) -> bool:
        """
        Set field value, identified by field index, from string
        Useful for iterating over fields
        """

        is_edited = True

        if field_idx == Operation.FieldIdx.DATE:
            try:
                self.operation.date = datetime.strptime(val_str, FMT_DATE)
            except ValueError:
                is_edited = False
        elif field_idx == Operation.FieldIdx.MODE:
            self.operation.mode = val_str
        elif field_idx == Operation.FieldIdx.TIER:
            self.operation.tier = val_str
        elif field_idx == Operation.FieldIdx.CAT:
            self.operation.cat = val_str
        elif field_idx == Operation.FieldIdx.DESC:
            self.operation.desc = val_str
        elif field_idx == Operation.FieldIdx.AMOUNT:
            try:
                self.operation.amount = float(val_str)
            except ValueError:
                is_edited = False

        return is_edited

    # def display(self):
    #     """
    #     Display
    #     """

    #     # Window border
    #     self.win.clear()
    #     self.win.border()
    #     self.win.move(0, 2)
    #     self.win.addstr(" OPERATION ", A_BOLD)

    #     # Init window cursor position
    #     (win_y, win_x) = (2, 2)

    #     # For each field
    #     for field_idx in range(self.operation.IDX_AMOUNT + 1):

    #         # Set display flag for highlighted field
    #         disp_flag = A_NORMAL
    #         if field_idx == self.ope_field_hl_idx:
    #             disp_flag = A_STANDOUT

    #         # Display field
    #         (name_str, val_str) = self.operation.get_field(field_idx)
    #         self.win.addstr(win_y, win_x, f"{name_str} : {val_str}", disp_flag)

    #         # Update window cursor position
    #         win_y = win_y + 1

    #     # Move cursor away from last field
    #     win_y = win_y + 1
    #     self.win.addstr(win_y, win_x, "")

    #     self.win.refresh()
