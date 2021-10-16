
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

    def copy(self):
        """
        Deep copy : Create and return new operation

        Returns:
            Operation: Created deep copy
        """

        return Operation(self.date, self.mode, self.tier, self.cat, self.desc, self.amount)

class OperationDispMgrCurses():
    """
    Curses operation display manager
    """

    def __init__(self, op: Operation) -> None:

        self.op: Operation = op

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
        for field_idx in range(self.op.IDX_AMOUNT + 1):

            # Set display flag for highlighted field
            disp_flag = A_NORMAL
            if field_idx == self.op_field_hl_idx:
                disp_flag = A_STANDOUT

            # Display field
            (name_str, val_str) = self.op.get_field(field_idx)
            self.win.addstr(win_y, win_x, f"{name_str} : {val_str}", disp_flag)

            # Update window cursor position
            win_y = win_y + 1

        # Move cursor away from last field
        win_y = win_y + 1
        self.win.addstr(win_y, win_x, "")

        self.win.refresh()

    def browse(self, win_main):
        """
        Browse
        """

        # Create window
        self.win = curses.newwin(20, 50, 10, 10)
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
                if self.op_field_hl_idx < self.op.IDX_DATE:
                    self.op_field_hl_idx = self.op.IDX_AMOUNT

            # Highlight next field
            elif key == "KEY_DOWN":
                self.op_field_hl_idx += 1
                if self.op_field_hl_idx > self.op.IDX_AMOUNT:
                    self.op_field_hl_idx = self.op.IDX_DATE

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
                    status = self.op.set_field(self.op_field_hl_idx, val_str)
                    if status == ERROR:
                        continue

                    # Field edited
                    is_edited = True

                    # Is date edited
                    if self.op_field_hl_idx == self.op.IDX_DATE:
                        is_date_edited = True

            # Exit
            elif key == '\x1b':
                break

        return (is_edited, is_date_edited)
