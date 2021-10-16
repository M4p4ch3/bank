
"""
Operation
"""

from datetime import datetime
from typing import Tuple

from utils import (OK, ERROR, FMT_DATE)

# Display
import curses
from curses import *

class Operation():
    """
    Operation
    """

    # Field index
    IDX_INVALID = -1
    IDX_DATE = 0
    IDX_MODE = 1
    IDX_TIER = 2
    IDX_CAT = 3
    IDX_DESC = 4
    IDX_AMOUNT = 5
    IDX_LAST = IDX_AMOUNT

    def __init__(self, op_date: datetime, mode: str,
                 tier: str, cat: str, desc: str, amount: float) -> None:

        self.date: datetime = op_date
        self.mode: str = mode
        self.tier: str = tier
        self.cat: str = cat
        self.desc: str = desc
        self.amount: float = amount

        # Display manager
        self.disp_mgr: OperationDispMgrCurses = OperationDispMgrCurses(self)

    def get_str(self, indent: int = 0) -> str:
        """
        Get string representation
        """

        indent_str = ""
        for _ in range(indent):
            indent_str += "    "

        ret = ""
        ret += f"{indent_str}date   : {self.date.strftime(FMT_DATE)}\n"
        ret += f"{indent_str}mode   : {self.mode}\n"
        ret += f"{indent_str}tier   : {self.tier}\n"
        ret += f"{indent_str}cat    : {self.cat}\n"
        ret += f"{indent_str}desc   : {self.desc}\n"
        ret += f"{indent_str}amount : {self.amount}"

        return ret

    def get_field(self, field_idx) -> Tuple[str, str]:
        """
        Get field (name, value), identified by field index
        Useful for iterating over fields
        """

        ret = ("", "")

        if field_idx == self.IDX_DATE:
            ret = ("date", self.date.strftime(FMT_DATE))
        elif field_idx == self.IDX_MODE:
            ret = ("mode", self.mode)
        elif field_idx == self.IDX_TIER:
            ret = ("tier", self.tier)
        elif field_idx == self.IDX_CAT:
            ret = ("cat", self.cat)
        elif field_idx == self.IDX_DESC:
            ret = ("desc", self.desc)
        elif field_idx == self.IDX_AMOUNT:
            ret = ("amount", str(self.amount))

        return ret

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
        elif field_idx == self.IDX_MODE:
            self.mode = val_str
        elif field_idx == self.IDX_TIER:
            self.tier = val_str
        elif field_idx == self.IDX_CAT:
            self.cat = val_str
        elif field_idx == self.IDX_DESC:
            self.desc = val_str
        elif field_idx == self.IDX_AMOUNT:
            try:
                self.amount = float(val_str)
            except ValueError:
                return ERROR

        return OK

class OperationDispMgrCurses():
    """
    Curses operation display manager
    """

    def __init__(self, op: Operation) -> None:
        self.op: Operation = op

    def display(self, win, field_hl_idx):
        """
        Display
        """

        win.clear()
        win.border()
        win.move(0, 2)
        win.addstr(" OPERATION ", A_BOLD)

        (y, x) = (2, 2)
        for field_idx in range(self.op.IDX_AMOUNT + 1):

            disp_flag = A_NORMAL
            if field_idx == field_hl_idx:
                disp_flag = A_STANDOUT

            (name_str, val_str) = self.op.get_field(field_idx)
            win.addstr(y, x, f"{name_str} : {val_str}", disp_flag)
            y = y + 1

        y = y + 1
        win.addstr(y, x, "")

        win.refresh()

    def browse(self, win):
        """
        Browse
        """

        is_edited = False
        is_date_edited = False
        field_hl_idx = 0

        while True:

            self.display(win, field_hl_idx)
            (y, _) = (win.getyx()[0], 2)
            y = y + 2

            key = win.getkey()

            # Highlight previous field
            if key == "KEY_UP":
                field_hl_idx = field_hl_idx - 1
                if field_hl_idx < self.op.IDX_DATE:
                    field_hl_idx = self.op.IDX_AMOUNT

            # Highlight next field
            elif key == "KEY_DOWN":
                field_hl_idx = field_hl_idx + 1
                if field_hl_idx > self.op.IDX_AMOUNT:
                    field_hl_idx = self.op.IDX_DATE

            # Edit highlighted field
            elif key == "\n":

                win.addstr("Value : ")
                win.keypad(False)
                curses.echo()
                val_str = win.getstr().decode(encoding="utf-8")
                win.keypad(True)
                curses.noecho()

                if val_str != "":

                    status = self.op.set_field(field_hl_idx, val_str)
                    if status == ERROR:
                        continue

                    # Field edited
                    is_edited = True
                    # If date edited
                    if field_hl_idx == self.op.IDX_DATE:
                        is_date_edited = True

            # Exit
            elif key == '\x1b':
                break

        return (is_edited, is_date_edited)
