"""
Display
"""

import curses
from curses import *
from datetime import datetime
from enum import IntEnum
import logging
from typing import (TYPE_CHECKING, Any, List)

from ..account import Account
from ..statement import Statement
from ..operation import Operation
from ..utils.clipboard import Clipboard
from ..utils.my_date import FMT_DATE
from ..utils.return_code import RetCode

if TYPE_CHECKING:
    from _curses import _CursesWindow
    Window = _CursesWindow
else:
    from typing import Any
    Window = Any

# Length for display padding
LEN_DATE = 10
LEN_NAME = LEN_DATE
LEN_MODE = 8
LEN_TIER = 18
LEN_CAT = 10
LEN_DESC = 34
LEN_AMOUNT = 8

class ColorPairId(IntEnum):
    """
    Curses color pair ID
    """

    RED_BLACK = 1
    GREEN_BLACK = 2

class WinId(IntEnum):
    """
    Window ID
    """

    MAIN = 0
    SUB = 1
    INFO = 2
    INPUT = 3
    # CMD = 4
    # STATUS = 5
    LAST = INPUT

class DispCurses():
    """
    Curses display
    """

    PADDING_Y = 0
    PADDING_X = 1
    BORDER_H = 1
    BORDER_W = BORDER_H

    def __init__(self, win_main: Window) -> None:

        self.logger = logging.getLogger("DispCurses")

        # Windows list
        self.win_list: List[Window] = [None] * (WinId.LAST + 1)

        # Item list clipboard
        self.item_list_clipboard: Clipboard = Clipboard()

        # Main window
        (win_main_h, win_main_w) = win_main.getmaxyx()
        self.win_list[WinId.MAIN] = win_main
        win_main.keypad(True)

        # Sub main window
        win_h = win_main_h - 2 * self.BORDER_H - 2 * self.PADDING_Y
        win_w = int(2 * win_main_w / 3) - 2 * self.BORDER_W
        win_y = self.BORDER_H + self.PADDING_Y
        win_x = self.BORDER_W + self.PADDING_X
        win = curses.newwin(win_h, win_w, win_y, win_x)
        self.win_list[WinId.SUB] = win
        win_sub_h = win_h

        # Info window
        win_h = int(win_sub_h / 2) - int(self.PADDING_Y / 2)
        win_w = int(win_main_w / 3) - 2 * self.BORDER_W - self.PADDING_X
        win_y = self.BORDER_H + self.PADDING_Y
        win_x = win_main_w - self.BORDER_W - win_w - self.PADDING_X
        win = curses.newwin(win_h, win_w, win_y, win_x)
        self.win_list[WinId.INFO] = win

        # Input window
        win_h = int(win_sub_h / 2) - int(self.PADDING_Y / 2)
        win_w = int(win_main_w / 3) - 2 * self.BORDER_W - self.PADDING_X
        win_y = win_main_h - self.BORDER_H - win_h - self.PADDING_Y
        win_x = win_main_w - self.BORDER_W - win_w - self.PADDING_X
        win = curses.newwin(win_h, win_w, win_y, win_x)
        self.win_list[WinId.INPUT] = win

        curses.init_pair(ColorPairId.RED_BLACK, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(ColorPairId.GREEN_BLACK, curses.COLOR_GREEN, curses.COLOR_BLACK)

class ContainerDispCurses():
    """
    Curses container (account, statement) display
    """

    ITEM_SEPARATOR = ""
    ITEM_HEADER = ""
    ITEM_MISSING = ""

    def __init__(self, disp: DispCurses) -> None:

        # Main display
        self.disp: DispCurses = disp

        self.item_hl:Any = None

        self.item_sel_list = [Any]

    def get_item_list(self) -> List[Any]:
        """
        Get item list
        """
        # To overload
        return []

    def add_item(self, item: Any) -> None:
        """
        Add item
        """
        # To overload

    def remove_item_list(self, item_list: List[Any]) -> RetCode:
        """
        Remove item list
        """
        # To overload
        return RetCode.OK

    def edit_item(self, item) -> None:
        """
        Edit item
        """

        field_focus_idx: int = 0

        while True:

            self.display_item_fields(item, field_focus_idx)

    def browse_item(self, item) -> None:
        """
        Browse item
        """
        # To overload

    def create_item(self) -> Any:
        """
        Create item
        """
        # To overload
        a: int = 0
        return a

    def copy(self) -> None:
        """
        Copy selected or highlited item(s)
        """

        if len(self.item_sel_list) > 0:
            item_list = self.item_sel_list
        elif self.item_hl is not None:
            item_list = [self.item_hl]
        else:
            return

        self.disp.item_list_clipboard.set(item_list)

    def cut(self) -> None:
        """
        Cut selected or highlited item(s)
        """

        if len(self.item_sel_list) > 0:
            item_list = self.item_sel_list
        elif self.item_hl is not None:
            item_list = [self.item_hl]
        else:
            return

        self.disp.item_list_clipboard.set(item_list)

        # If highlighted item in buffer
        if self.item_hl in item_list:
            # Highlight closest item
            # TODO
            # self.item_hl = self.get_closest_item(item_list)
            item_list: List[Any] = self.get_item_list()
            self.item_hl = item_list[0]

        # Remove items list
        for item in item_list:
            self.remove_item(item)

    def paste(self) -> None:
        """
        Paste item(s)
        """

        item_list = self.disp.item_list_clipboard.get()
        if item_list is None or len(item_list) == 0:
            return

        # Add item list
        for item in item_list:
            self.add_item(item)

    def save(self) -> None:
        """
        Save
        """
        # To overload

    def exit(self) -> RetCode:
        """
        Exit
        """
        # To overload
        return RetCode.OK

    def display_info(self) -> None:
        """
        Display info
        """
        # To overload

    def display_item_fields(self, item, field_focus_idx: int) -> None:
        """
        Display fields
        """

        win: Window = self.disp.win_list[WinId.INPUT]

        for field_idx in range(item.FieldIdx.LAST):

            (name, value) = item.get_field(field_idx)

            win.addstr(name)
            win.addstr(value)

        win.refresh()

    def display_item_line(self, item, win: Window,
                          win_y: int, win_x: int, flag) -> None:
        """
        Display item line
        """
        # To overload

    def display_item_list(self, item_focus_idx: int,
                          hl_changed: bool, focus_changed: bool) -> None:
        """
        Display list of items (statements or operations)

        Args:
            item_focus_idx (int): Focused item
            hl_changed (bool): Is highlighted item updated
            focus_changed (bool): Is focused item updated
        """

        item_list: List[Any] = self.get_item_list()

        # Sub main window
        win: Window = self.disp.win_list[WinId.SUB]
        win_h: int = win.getmaxyx()[0]

        # Number of displayed items
        item_disp_nb: int = win_h - 4
        if len(item_list) < item_disp_nb:
            item_disp_nb = len(item_list)

        # If highlighted item updated
        if hl_changed:

            # Fix focus

            item_hl_idx = item_list.index(self.item_hl)

            if item_hl_idx < item_focus_idx:

                # Move focus up
                item_focus_idx -= 1
                if item_focus_idx < 0:
                    item_focus_idx = 0

            elif item_hl_idx > item_focus_idx + item_disp_nb - 1:

                # Move focus down
                item_focus_idx += 1
                if item_focus_idx > len(item_list) - item_disp_nb:
                    item_focus_idx = len(item_list) - item_disp_nb

        # Else, if focus updated
        elif focus_changed:

            # Fix focus

            if item_focus_idx < 0:
                item_focus_idx = 0
            elif item_focus_idx > len(item_list) - item_disp_nb:
                item_focus_idx = len(item_list) - item_disp_nb

            # Fix highlighted item

            item_hl_idx = item_list.index(self.item_hl)

            if item_hl_idx < item_focus_idx:

                # Highlight first displayed item
                item_hl_idx = item_focus_idx
                self.item_hl = item_list[item_hl_idx]

            elif item_hl_idx > item_focus_idx + item_disp_nb - 1:

                # Highlight last displayed item
                item_hl_idx = item_focus_idx + item_disp_nb - 1
                self.item_hl = item_list[item_hl_idx]

        item_separator = self.ITEM_SEPARATOR
        item_header = self.ITEM_HEADER
        item_missing = self.ITEM_MISSING

        (win_y, win_x) = (0, 0)

        # Item separator
        win.addstr(win_y, win_x, item_separator)
        win_y += 1

        # Item header
        win.addstr(win_y, win_x, item_header)
        win_y += 1

        # TODO merge to common case
        if len(item_list) == 0:
            win.addstr(win_y, win_x, item_separator)
            win_y += 1
            win.addstr(win_y, win_x, item_separator)
            win_y += 1
            win.refresh()
            return

        # Item separator or missing
        if item_focus_idx == 0:
            win.addstr(win_y, win_x, item_separator)
        else:
            win.addstr(win_y, win_x, item_missing)
        win_y += 1

        # Item list
        for item_idx in range(item_focus_idx, item_focus_idx + item_disp_nb):

            if item_idx >= len(item_list):
                break

            item = item_list[item_idx]

            disp_flag = A_NORMAL
            if item == self.item_hl:
                disp_flag += A_STANDOUT
            if item in self.item_sel_list:
                disp_flag += A_BOLD

            self.display_item_line(item, win, win_y, win_x, disp_flag)
            win_y += 1

        # Item separator or missing
        if item_idx == len(item_list) - 1:
            win.addstr(win_y, win_x, item_separator)
        else:
            win.addstr(win_y, win_x, item_missing)
        win_y += 1

        if len(item_list) != 0:
            op_disp_ratio = item_disp_nb / len(item_list)

        # Slider
        (win_y, win_x) = (3, win.getyx()[1])
        for _ in range(0, int(item_focus_idx * op_disp_ratio)):
            win.addstr(win_y, win_x, " ")
            win_y += 1
        for _ in range(int(item_focus_idx * op_disp_ratio),
                       int((item_focus_idx + item_disp_nb) * op_disp_ratio)):
            win.addstr(win_y, win_x, " ", A_STANDOUT)
            win_y += 1
        for _ in range(int((item_focus_idx + item_disp_nb) * op_disp_ratio),
                       int((len(item_list)) * op_disp_ratio)):
            win.addstr(win_y, win_x, " ")
            win_y += 1

        win.refresh()

    def browse(self):
        """
        Browse
        """

        # Init
        item_list: List[Any] = self.get_item_list()
        item_focus_idx: int = 0
        if len(item_list) != 0:
            self.item_hl = item_list[0]
        else:
            self.item_hl = None
        self.item_sel_list = []

        # Main window
        win: Window = self.disp.win_list[WinId.MAIN]
        win.clear()
        win.border()
        win.move(0, 2)
        win.addstr(" STATEMENT ", A_BOLD)
        win.refresh()

        # Display info
        self.display_info()

        # Display item list
        self.display_item_list(item_focus_idx, False, False)

        while True:

            item_list: List[Any] = self.get_item_list()

            hl_changed = False
            focus_changed = False

            key = win.getkey()

            # Highlight previous item
            if key == "KEY_UP":
                if self.item_hl is None:
                    continue
                op_hl_idx = item_list.index(self.item_hl) - 1
                if op_hl_idx < 0:
                    op_hl_idx = 0
                    continue
                self.item_hl = item_list[op_hl_idx]
                hl_changed = True

            # Highlight next item
            elif key == "KEY_DOWN":
                if self.item_hl is None:
                    continue
                op_hl_idx = item_list.index(self.item_hl) + 1
                if op_hl_idx >= len(item_list):
                    op_hl_idx = len(item_list) - 1
                    continue
                self.item_hl = item_list[op_hl_idx]
                hl_changed = True

            # Focus previous item
            elif key == "KEY_PPAGE":
                if self.item_hl is None:
                    continue
                item_focus_idx -= 3
                focus_changed = True

            # Focus next item
            elif key == "KEY_NPAGE":
                if self.item_hl is None:
                    continue
                item_focus_idx += 3
                focus_changed = True

            # Trigger item selection
            elif key == " ":
                if self.item_hl is None:
                    continue
                if self.item_hl not in self.item_sel_list:
                    self.item_sel_list.append(self.item_hl)
                else:
                    self.item_sel_list.remove(self.item_hl)

            # Copy item(s)
            elif key == "c":
                self.copy()

            # Cut item(s)
            elif key == "x":
                self.cut()

            # Paste item(s)
            elif key == "v":
                self.paste()

            # Edit highlighted item
            elif key == "e":
                self.edit_item(self.item_hl)

            # Open highlighted item
            elif key == "\n":
                self.browse_item(self.item_hl)

            # Add new item
            elif key in ("KEY_IC", "+"):
                item = self.create_item()
                if item is not None:
                    self.add_item(item)

            # Remove item(s)
            elif key in ("KEY_DC", "-"):
                ret = RetCode.CANCELED
                if len(self.item_sel_list) != 0:
                    ret = self.remove_item_list(self.item_sel_list)
                elif self.item_hl is not None:
                    ret = self.remove_item_list([self.item_hl])

            # Save
            elif key == "s":
                self.save()

            # Exit
            elif key == '\x1b':
                ret = self.exit()
                if ret == RetCode.OK:
                    break

            # Display info
            self.display_info()

            # Display item list
            self.display_item_list(item_focus_idx, hl_changed, focus_changed)

class AccountDispCurses(ContainerDispCurses):
    """
    Curses account display
    """

    # Item separator
    ITEM_SEPARATOR = "|"
    ITEM_SEPARATOR += "-" + "-".ljust(LEN_NAME, "-") + "-|"
    ITEM_SEPARATOR += "-" + "-".ljust(LEN_DATE, "-") + "-|"
    ITEM_SEPARATOR += "-" + "-".ljust(LEN_AMOUNT, "-") + "-|"
    ITEM_SEPARATOR += "-" + "-".ljust(LEN_AMOUNT, "-") + "-|"
    ITEM_SEPARATOR += "-" + "-".ljust(LEN_AMOUNT, "-") + "-|"
    ITEM_SEPARATOR += "-" + "-".ljust(LEN_AMOUNT, "-") + "-|"

    # Item header
    ITEM_HEADER = "|"
    ITEM_HEADER += " " + "name".ljust(LEN_DATE, " ") + " |"
    ITEM_HEADER += " " + "date".ljust(LEN_DATE, " ") + " |"
    ITEM_HEADER += " " + "start".ljust(LEN_AMOUNT, " ") + " |"
    ITEM_HEADER += " " + "end".ljust(LEN_AMOUNT, " ") + " |"
    ITEM_HEADER += " " + "diff".ljust(LEN_AMOUNT, " ") + " |"
    ITEM_HEADER += " " + "error".ljust(LEN_AMOUNT, " ") + " |"

    # Item missing
    ITEM_MISSING = "|"
    ITEM_MISSING += " " + "...".ljust(LEN_NAME, " ") + " |"
    ITEM_MISSING += " " + "...".ljust(LEN_DATE, " ") + " |"
    ITEM_MISSING += " " + "...".ljust(LEN_AMOUNT, " ") + " |"
    ITEM_MISSING += " " + "...".ljust(LEN_AMOUNT, " ") + " |"
    ITEM_MISSING += " " + "...".ljust(LEN_AMOUNT, " ") + " |"

    def __init__(self, account: Account, disp: DispCurses) -> None:

        self.logger = logging.getLogger("AccountDispCurses")

        # Init container display
        super().__init__(disp)

        # Account
        self.account: Account = account

    def get_item_list(self) -> List[Statement]:
        """
        Get statement list
        """
        return self.account.stat_list

    def add_item(self, stat: Statement) -> None:
        """
        Add statement
        """
        self.account.add_stat(stat)

    def remove_item_list(self, stat_list: List[Statement]) -> None:
        """
        Remove statement list
        """

        # Input window
        win = self.disp.win_list[WinId.INPUT]
        win.clear()
        win.border()
        win.addstr(0, 2, " REMOVE STATEMENTS ", A_BOLD)
        win.addstr(2, 2, f"Remove {len(stat_list)} statements")

        # Ask for remove confirm
        win.addstr(4, 2, "Confirm ? (y/n) : ")
        confirm_char = win.getch()

        if confirm_char != ord('y'):
            # Canceled
            return RetCode.CANCELED

        # Confirmed
        self.account.remove_stat_list(stat_list)
        return OK

    def browse_item(self, stat: Statement) -> None:
        """
        Browse statement
        """

        # Init statement display
        stat_disp: StatementDispCurses = StatementDispCurses(stat, self.disp)

        # Browse statement
        stat_disp.browse()

    def create(self) -> Statement:
        """
        Create statement
        """

        # Init statement
        stat: Statement = Statement(datetime.now(), 0.0, 0.0)

        # Init statement display
        stat_disp: StatementDispCurses = StatementDispCurses(stat, self.disp)

        # Set statement fields
        stat_disp.set_fields()

        return stat

    def display_item_line(self, stat: Statement, win: Window,
                          win_y: int, win_x: int, flag) -> None:

        win.addstr(win_y, win_x, "| ")
        win.addstr(stat.date.strftime(FMT_DATE).ljust(LEN_NAME), flag)
        win.addstr(" | ")
        win.addstr(stat.date.strftime(FMT_DATE).ljust(LEN_DATE), flag)
        win.addstr(" | ")
        win.addstr(str(stat.bal_start).ljust(LEN_AMOUNT), flag)
        win.addstr(" | ")
        win.addstr(str(stat.bal_end).ljust(LEN_AMOUNT), flag)
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

    # # TODO rework like operation.set_fields
    # def add_stat(self) -> int:
    #     """
    #     Add statement
    #     """

    #     # Use input window
    #     win: Window = self.disp.win_list[WinId.INPUT]

    #     win.clear()
    #     win.border()
    #     win.move(0, 2)
    #     win.addstr(" STATEMENT ", A_BOLD)

    #     (win_y, win_x) = (2, 2)
    #     win.addstr(win_y, win_x, "date : ")
    #     win_y = win_y + 1
    #     win.addstr(win_y, win_x, "start balance : ")
    #     win_y = win_y + 1
    #     win.addstr(win_y, win_x, "end balance   : ")
    #     win_y = win_y + 1

    #     win.keypad(False)
    #     curses.echo()

    #     (win_y, win_x) = (2, 2)

    #     is_converted = False
    #     while not is_converted:
    #         win.addstr(win_y, win_x, "date :                  ")
    #         win.addstr(win_y, win_x, "date : ")
    #         val_str = win.getstr().decode(encoding="utf-8")
    #         try:
    #             date = datetime.strptime(val_str, FMT_DATE)
    #             is_converted = True
    #         except ValueError:
    #             pass

    #     win_y = win_y + 1

    #     is_converted = False
    #     while not is_converted:
    #         win.addstr(win_y, win_x, "start balance :         ")
    #         win.addstr(win_y, win_x, "start balance : ")
    #         val_str = win.getstr().decode(encoding="utf-8")
    #         try:
    #             bal_start = float(val_str)
    #             is_converted = True
    #         except ValueError:
    #             pass

    #     win_y = win_y + 1

    #     is_converted = False
    #     while not is_converted:
    #         win.addstr(win_y, win_x, "end balance :           ")
    #         win.addstr(win_y, win_x, "end balance : ")
    #         val_str = win.getstr().decode(encoding="utf-8")
    #         try:
    #             bal_end = float(val_str)
    #             is_converted = True
    #         except ValueError:
    #             pass

    #     win_y = win_y + 1

    #     win.keypad(True)
    #     curses.noecho()

    #     # Init statement
    #     stat = Statement(date.strftime(FMT_DATE), bal_start, bal_end)

    #     # Create statement file
    #     ret = stat.create_file()
    #     if ret != OK:
    #         self.logger.error("add_stat : Create statement file FAILED")
    #         return ret

    #     # Append statement to statements list
    #     self.account.insert_stat(stat)

    #     return OK

    # def delete_stat(self, stat: Statement) -> None:
    #     """
    #     Delete statement
    #     """

    #     # Input window
    #     win: Window = self.disp.win_list[WinId.INPUT]
    #     win.clear()
    #     win.border()
    #     win.addstr(0, 2, " DELETE STATEMENT ", A_BOLD)
    #     win.addstr(2, 2, "Confirm ? (y/n) : ")
    #     confirm_c = win.getch()
    #     if confirm_c != ord('win_y'):
    #         win.addstr(7, 2, "Canceled", curses.color_pair(ColorPairId.RED_BLACK))
    #         win.refresh()
    #         return

    #     # Delete highlighted statement
    #     self.account.del_stat(stat)

class StatementDispCurses(ContainerDispCurses):
    """
    Curses statement display
    """

    # Item separator
    ITEM_SEPARATOR = "|"
    ITEM_SEPARATOR += "-" + "-".ljust(LEN_DATE, "-") + "-|"
    ITEM_SEPARATOR += "-" + "-".ljust(LEN_MODE, "-") + "-|"
    ITEM_SEPARATOR += "-" + "-".ljust(LEN_TIER, "-") + "-|"
    ITEM_SEPARATOR += "-" + "-".ljust(LEN_CAT, "-") + "-|"
    ITEM_SEPARATOR += "-" + "-".ljust(LEN_DESC, "-") + "-|"
    ITEM_SEPARATOR += "-" + "-".ljust(LEN_AMOUNT, "-") + "-|"

    # Item header
    ITEM_HEADER = "|"
    ITEM_HEADER += " " + "date".ljust(LEN_DATE, " ") + " |"
    ITEM_HEADER += " " + "mode".ljust(LEN_MODE, " ") + " |"
    ITEM_HEADER += " " + "tier".ljust(LEN_TIER, " ") + " |"
    ITEM_HEADER += " " + "cat".ljust(LEN_CAT, " ") + " |"
    ITEM_HEADER += " " + "desc".ljust(LEN_DESC, " ") + " |"
    ITEM_HEADER += " " + "amount".ljust(LEN_AMOUNT, " ") + " |"

    # Item missing
    ITEM_MISSING = "|"
    ITEM_MISSING += " " + "...".ljust(LEN_DATE, ' ') + " |"
    ITEM_MISSING += " " + "...".ljust(LEN_MODE, ' ') + " |"
    ITEM_MISSING += " " + "...".ljust(LEN_TIER, ' ') + " |"
    ITEM_MISSING += " " + "...".ljust(LEN_CAT, ' ') + " |"
    ITEM_MISSING += " " + "...".ljust(LEN_DESC, ' ') + " |"
    ITEM_MISSING += " " + "...".ljust(LEN_AMOUNT, ' ') + " |"

    def __init__(self, stat: Statement, disp: DispCurses) -> None:

        self.logger = logging.getLogger("StatementDispCurses")

        # Init container display
        super().__init__(disp)

        # Statement
        self.stat: Statement = stat

    def get_item_list(self) -> List[Operation]:
        """
        Get operation list
        """
        return self.stat.op_list

    def add_item(self, op: Operation) -> None:
        """
        Add operation
        """
        self.stat.add_op(op)

    def remove_item_list(self, op_list: List[Operation]) -> RetCode:
        """
        Remove operation list
        """

        # Input window
        win = self.disp.win_list[WinId.INPUT]
        win.clear()
        win.border()
        win.addstr(0, 2, " REMOVE OPERATIONS ", A_BOLD)
        win.addstr(2, 2, f"Remove {len(op_list)} operations")

        # Ask for remove confirm
        win.addstr(4, 2, "Confirm ? (y/n) : ")
        confirm_char = win.getch()

        if confirm_char != ord('y'):
            # Canceled
            return RetCode.CANCELED

        # Confirmed
        self.stat.remove_op_list(op_list)
        return OK

    def browse_item(self, operation: Operation) -> None:
        """
        Browse statement
        """

        # Init statement display
        stat_disp: StatementDispCurses = StatementDispCurses(stat, self.disp)

        # Browse statement
        stat_disp.browse()

    def create(self) -> Statement:
        """
        Create statement
        """

        # Init statement
        stat: Statement = Statement(datetime.now(), 0.0, 0.0)

        # Init statement display
        stat_disp: StatementDispCurses = StatementDispCurses(stat, self.disp)

        # Set statement fields
        stat_disp.set_fields()

        return stat

    def display_item_line(self, stat: Statement, win: Window,
                          win_y: int, win_x: int, flag) -> None:

        win.addstr(win_y, win_x, "| ")
        win.addstr(stat.date.strftime(FMT_DATE).ljust(LEN_NAME), flag)
        win.addstr(" | ")
        win.addstr(stat.date.strftime(FMT_DATE).ljust(LEN_DATE), flag)
        win.addstr(" | ")
        win.addstr(str(stat.bal_start).ljust(LEN_AMOUNT), flag)
        win.addstr(" | ")
        win.addstr(str(stat.bal_end).ljust(LEN_AMOUNT), flag)
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

    # def display_op_list(self, hl_changed: bool, focus_changed: bool) -> None:
    #     """
    #     Display operations list
    #     """

    #     # Sub main window
    #     win_sub: Window = self.disp.win_list[WinId.SUB]
    #     win_sub_h: int = win_sub.getmaxyx()[0]

    #     # Number of displayed operations
    #     op_disp_nb: int = win_sub_h - 4
    #     if len(self.stat.op_list) < op_disp_nb:
    #         op_disp_nb = len(self.stat.op_list)

    #     # If highlighted operation updated
    #     if hl_changed:

    #         # Fix focus

    #         op_hl_idx = self.stat.op_list.index(self.op_hl)

    #         if op_hl_idx < self.op_focus_idx:

    #             # Move focus up
    #             self.op_focus_idx -= 1
    #             if self.op_focus_idx < 0:
    #                 self.op_focus_idx = 0

    #         elif op_hl_idx > self.op_focus_idx + op_disp_nb - 1:

    #             # Move focus down
    #             self.op_focus_idx += 1
    #             if self.op_focus_idx > len(self.stat.op_list) - op_disp_nb:
    #                 self.op_focus_idx = len(self.stat.op_list) - op_disp_nb

    #     # Else, if focus updated
    #     elif focus_changed:

    #         # Fix focus

    #         if self.op_focus_idx < 0:
    #             self.op_focus_idx = 0
    #         elif self.op_focus_idx > len(self.stat.op_list) - op_disp_nb:
    #             self.op_focus_idx = len(self.stat.op_list) - op_disp_nb

    #         # Fix highlighted operation

    #         op_hl_idx = self.stat.op_list.index(self.op_hl)

    #         if op_hl_idx < self.op_focus_idx:

    #             # Highlight first displayed operation
    #             op_hl_idx = self.op_focus_idx
    #             self.op_hl = self.stat.op_list[op_hl_idx]

    #         elif op_hl_idx > self.op_focus_idx + op_disp_nb - 1:

    #             # Highlight last displayed operation
    #             op_hl_idx = self.op_focus_idx + op_disp_nb - 1
    #             self.op_hl = self.stat.op_list[op_hl_idx]

    #     (win_y, win_x) = (0, 0)

    #     # Operation separator
    #     win_sub.addstr(win_y, win_x, self.SEPARATOR)
    #     win_y += 1

    #     # Operations header
    #     win_sub.addstr(win_y, win_x, self.HEADER)
    #     win_y += 1

    #     if len(self.stat.op_list) == 0:
    #         win_sub.addstr(win_y, win_x, self.SEPARATOR)
    #         win_y += 1
    #         win_sub.addstr(win_y, win_x, self.SEPARATOR)
    #         win_y += 1
    #         win_sub.refresh()
    #         return

    #     # Operation separator or missing
    #     if self.op_focus_idx == 0:
    #         win_sub.addstr(win_y, win_x, self.SEPARATOR)
    #     else:
    #         win_sub.addstr(win_y, win_x, self.MISSING)
    #     win_y += 1

    #     # Operations list
    #     for op_idx in range(self.op_focus_idx, self.op_focus_idx + op_disp_nb):

    #         if op_idx >= len(self.stat.op_list):
    #             break

    #         operation = self.stat.op_list[op_idx]

    #         disp_flag = A_NORMAL
    #         if operation == self.op_hl:
    #             disp_flag += A_STANDOUT
    #         if operation in self.op_sel_list:
    #             disp_flag += A_BOLD

    #         op_str = "|"
    #         op_str += " " + operation.date.strftime(FMT_DATE)[:LEN_DATE].ljust(LEN_DATE, ' ') + " |"
    #         op_str += " " + operation.mode.ljust(LEN_MODE, ' ') + " |"
    #         op_str += " " + operation.tier[:LEN_TIER].ljust(LEN_TIER, ' ') + " |"
    #         op_str += " " + operation.cat[:LEN_CAT].ljust(LEN_CAT, ' ') + " |"
    #         op_str += " " + operation.desc[:LEN_DESC].ljust(LEN_DESC, ' ') + " |"
    #         op_str += " " + str(operation.amount)[:LEN_AMOUNT].ljust(LEN_AMOUNT, ' ') + " |"
    #         win_sub.addstr(win_y, win_x, op_str, disp_flag)
    #         win_y += 1

    #     # Operation separator or missing
    #     if op_idx == len(self.stat.op_list) - 1:
    #         win_sub.addstr(win_y, win_x, self.SEPARATOR)
    #     else:
    #         win_sub.addstr(win_y, win_x, self.MISSING)
    #     win_y += 1

    #     if len(self.stat.op_list) != 0:
    #         op_disp_ratio = op_disp_nb / len(self.stat.op_list)

    #     # Slider
    #     (win_y, win_x) = (3, win_sub.getyx()[1])
    #     for _ in range(0, int(self.op_focus_idx * op_disp_ratio)):
    #         win_sub.addstr(win_y, win_x, " ")
    #         win_y += 1
    #     for _ in range(int(self.op_focus_idx * op_disp_ratio),
    #                    int((self.op_focus_idx + op_disp_nb) * op_disp_ratio)):
    #         win_sub.addstr(win_y, win_x, " ", A_STANDOUT)
    #         win_y += 1
    #     for _ in range(int((self.op_focus_idx + op_disp_nb) * op_disp_ratio),
    #                    int((len(self.stat.op_list)) * op_disp_ratio)):
    #         win_sub.addstr(win_y, win_x, " ")
    #         win_y += 1

    #     win_sub.refresh()

    def display_info(self) -> None:
        """
        Display statement info
        """

        # Info window
        win_info: Window = self.disp.win_list[WinId.INFO]

        win_info.clear()
        win_info.border()
        win_info.addstr(0, 2, " INFO ", A_BOLD)

        (win_y, win_x) = (2, 2)
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

        win_info.addstr(win_y, win_x,
                        f"clipboard : {self.disp.item_list_clipboard.get_len()} operations")
        win_y += 1

        win_info.refresh()

    # def display_commands(self) -> None:

    #     win: Window = self.disp.win_list[WinId.CMD]
    #     win.clear()
    #     win.border()
    #     win.addstr(0, 2, " COMMANDS ", A_BOLD)
    #     cmd_str = "Add : INS/+, Del : DEL/-"
    #     cmd_str = cmd_str + ", Dupl : D, (Un)sel : SPACE, Move : M "
    #     cmd_str = cmd_str + ", Open : ENTER"
    #     cmd_str = cmd_str + ", Save : S, Ret : ESCAPE"
    #     win.addstr(1, 2, cmd_str)
    #     win.refresh()

    def browse_op(self) -> None:
        """
        Browse highlighted operation
        """

        # Browse highlighted operation
        op_disp: OperationDispCurses = OperationDispCurses(
            self.op_hl, self.disp.win_list[WinId.INPUT])
        (is_edited, is_date_edited) = op_disp.browse()

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

        # Set operation fields using display
        op_disp: OperationDispCurses = OperationDispCurses(
            operation, self.disp.win_list[WinId.INPUT])
        op_disp.set_fields()

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
        win = self.disp.win_list[WinId.INPUT]
        win.clear()
        win.border()
        win.addstr(0, 2, " DELETE OPERATIONS ", A_BOLD)
        win.addstr(2, 2, f"Delete {len(op_del_list)} operations")
        win.addstr(4, 2, "Confirm ? (y/n) : ")
        confirm_c = win.getch()
        if confirm_c != ord('y'):
            win.addstr(7, 2, "Canceled", curses.color_pair(ColorPairId.RED_BLACK))
            win.refresh()
            return

        # Delete operations from statement
        self.stat.del_op_list(op_del_list)

        # Clear selected operations
        self.op_sel_list.clear()

    def exit(self) -> RetCode:
        """
        Exit statement browse
        """

        # If saved
        if not self.stat.is_unsaved:
            # Exit
            return RetCode.OK

        # Unsaved changes

        # Input window
        win: Window = self.disp.win_list[WinId.INPUT]
        win.clear()
        win.border()
        win.addstr(0, 2, " UNSAVED CHANGES ", A_BOLD)

        # Ask for exit
        win.addstr(2, 2, "Exit ? (y/n) : ")
        char = win.getch()
        # Cancel
        if char == ord('n'):
            return RetCode.CANCELED

        # Ask for save
        win.addstr(2, 2, "Save ? (y/n) : ")
        char = win.getch()
        # Discard
        if char == ord('n'):
            self.stat.import_file()
        # Save
        else:
            self.stat.export_file()

        return RetCode.OK

    def set_fields(self) -> None:
        """
        Iterate over fields and set
        """

        # Input window
        win: Window = self.disp.win_list[WinId.INPUT]
        win.keypad(True)

        # For each field
        for field_idx in range(self.stat.IDX_BAL_END + 1):

            # Highlight current field
            self.op_field_hl_idx = field_idx

            # Display
            self.display()
            (win_y, win_x) = (self.win.getyx()[0], 2)

            # Get value
            self.win.addstr(win_y, win_x, "Value : ")
            self.win.keypad(False)
            curses.echo()
            val_str = self.win.getstr().decode(encoding="utf-8")
            self.win.keypad(True)
            curses.noecho()

            # Set value
            if val_str != "":
                self.operation.set_field(field_idx, val_str)

    # def browse(self) -> None:
    #     """
    #     Browse
    #     """

    #     # Init
    #     self.op_focus_idx: int = 0
    #     if len(self.stat.op_list) != 0:
    #         self.op_hl = self.stat.op_list[0]
    #     else:
    #         self.op_hl = None
    #     self.op_sel_list = []

    #     # Main window
    #     win_main: Window = self.disp.win_list[WinId.MAIN]
    #     win_main.clear()
    #     win_main.border()
    #     win_main.move(0, 2)
    #     win_main.addstr(" STATEMENT ", A_BOLD)
    #     win_main.refresh()

    #     # Display statement info
    #     self.display_info()

    #     # Display commands
    #     # self.display_commands()

    #     # Display operations list
    #     self.disp.display_item_list(self.stat.op_list, self.op_focus_idx,
    #                                 self.op_hl, self.op_sel_list,
    #                                 False, False)

    #     while True:

    #         info_updated = False
    #         hl_changed = False
    #         focus_changed = False

    #         key = self.disp.win_list[WinId.MAIN].getkey()

    #         # Highlight previous operation
    #         if key == "KEY_UP":
    #             if self.op_hl is None:
    #                 continue
    #             op_hl_idx = self.stat.op_list.index(self.op_hl) - 1
    #             if op_hl_idx < 0:
    #                 op_hl_idx = 0
    #                 continue
    #             self.op_hl = self.stat.op_list[op_hl_idx]
    #             hl_changed = True

    #         # Highlight next operation
    #         elif key == "KEY_DOWN":
    #             if self.op_hl is None:
    #                 continue
    #             op_hl_idx = self.stat.op_list.index(self.op_hl) + 1
    #             if op_hl_idx >= len(self.stat.op_list):
    #                 op_hl_idx = len(self.stat.op_list) - 1
    #                 continue
    #             self.op_hl = self.stat.op_list[op_hl_idx]
    #             hl_changed = True

    #         # Focus previous operations
    #         elif key == "KEY_PPAGE":
    #             if self.op_hl is None:
    #                 continue
    #             self.op_focus_idx -= 3
    #             focus_changed = True

    #         # Focus next operations
    #         elif key == "KEY_NPAGE":
    #             if self.op_hl is None:
    #                 continue
    #             self.op_focus_idx += 3
    #             focus_changed = True

    #         # Trigger operation selection
    #         elif key == " ":
    #             if self.op_hl is None:
    #                 continue
    #             if self.op_hl not in self.op_sel_list:
    #                 self.op_sel_list.append(self.op_hl)
    #             else:
    #                 self.op_sel_list.remove(self.op_hl)

    #         # Copy operations(s)
    #         elif key == "c":
    #             self.copy_op_list()
    #             info_updated = True

    #         # Cut operation(s)
    #         elif key == "x":
    #             self.cut_op_list()
    #             info_updated = True

    #         # Paste operation(s)
    #         elif key == "v":
    #             self.paste_op_list()
    #             info_updated = True

    #         # Open highlighted operation
    #         elif key == "\n":
    #             self.browse_op()
    #             info_updated = True

    #         # Add operation
    #         elif key in ("KEY_IC", "+"):
    #             self.add_op()
    #             info_updated = True

    #         # Delete operation(s)
    #         elif key in ("KEY_DC", "-"):
    #             self.delete_op()
    #             info_updated = True

    #         # Save
    #         elif key == "s":
    #             self.stat.export_file()
    #             info_updated = True

    #         # Exit
    #         elif key == '\x1b':
    #             self.exit()
    #             break

    #         if info_updated:
    #             # Display statement info
    #             self.display_info()

    #         # Display commands
    #         # self.display_commands()

    #         # Display operations list
    #         self.disp.display_item_list(self.stat.op_list, self.op_focus_idx,
    #                                     self.op_hl, self.op_sel_list,
    #                                     hl_changed, focus_changed)

class OperationDispCurses():
    """
    Curses operation display
    """

    def __init__(self, operation: Operation, win: Window) -> None:

        # Operation
        self.operation: Operation = operation

        # Window
        self.win: Window = win

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
        for field_idx in range(self.operation.IDX_AMOUNT + 1):

            # Set display flag for highlighted field
            disp_flag = A_NORMAL
            if field_idx == self.op_field_hl_idx:
                disp_flag = A_STANDOUT

            # Display field
            (name_str, val_str) = self.operation.get_field(field_idx)
            self.win.addstr(win_y, win_x, f"{name_str} : {val_str}", disp_flag)

            # Update window cursor position
            win_y = win_y + 1

        # Move cursor away from last field
        win_y = win_y + 1
        self.win.addstr(win_y, win_x, "")

        self.win.refresh()

    def browse(self):
        """
        Browse
        """

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
                if self.op_field_hl_idx < self.operation.IDX_DATE:
                    self.op_field_hl_idx = self.operation.IDX_AMOUNT

            # Highlight next field
            elif key == "KEY_DOWN":
                self.op_field_hl_idx += 1
                if self.op_field_hl_idx > self.operation.IDX_AMOUNT:
                    self.op_field_hl_idx = self.operation.IDX_DATE

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
                    is_edited_single = self.operation.set_field(self.op_field_hl_idx, val_str)
                    if is_edited_single:
                        is_edited = True
                        if self.op_field_hl_idx == self.operation.IDX_DATE:
                            is_date_edited = True

            # Exit
            elif key == '\x1b':
                break

        return (is_edited, is_date_edited)

    def set_fields(self) -> None:
        """
        Iterate over fields and set
        """

        self.win.keypad(True)

        # For each field
        for field_idx in range(self.operation.IDX_AMOUNT + 1):

            # Highlight current field
            self.op_field_hl_idx = field_idx

            # Display
            self.display()
            (win_y, win_x) = (self.win.getyx()[0], 2)

            # Get value
            self.win.addstr(win_y, win_x, "Value : ")
            self.win.keypad(False)
            curses.echo()
            val_str = self.win.getstr().decode(encoding="utf-8")
            self.win.keypad(True)
            curses.noecho()

            # Set value
            if val_str != "":
                self.operation.set_field(field_idx, val_str)
