"""
Display
"""

import curses
from curses import *
from datetime import datetime
from enum import IntEnum
import logging
from typing import (TYPE_CHECKING, Any, List, Union, Tuple)

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
    LEFT = 1
    RIGHT_TOP = 2
    RIGHT_BOT = 3
    LAST = RIGHT_BOT

class NoOverrideError(Exception):
    """
    Exception raised for not overriden method
    """

    def __init__(self, base_class: str = "", derived_class: str = "", method: str = "") -> None:
        msg = f"{base_class}.{method} not overriden in {derived_class}"
        super().__init__(msg)

class DispCurses():
    """
    Curses display
    """

    PADDING_Y = 0
    PADDING_X = 1
    BORDER_H = 1
    BORDER_W = BORDER_H

    def __init__(self, win_main: Window) -> None:

        # Windows list
        self.win_list: List[Window] = [None] * (WinId.LAST + 1)

        # Item list clipboard
        self.item_list_clipboard: Clipboard = Clipboard()

        # Main window
        (win_main_h, win_main_w) = win_main.getmaxyx()
        self.win_list[WinId.MAIN] = win_main
        win_main.keypad(True)

        # Left main window
        win_h = win_main_h - 2 * self.BORDER_H - 2 * self.PADDING_Y
        win_w = int(2 * win_main_w / 3) - 2 * self.BORDER_W
        win_y = self.BORDER_H + self.PADDING_Y
        win_x = self.BORDER_W + self.PADDING_X
        win = curses.newwin(win_h, win_w, win_y, win_x)
        self.win_list[WinId.LEFT] = win
        win_left_h = win_h

        # Top right window
        win_h = int(win_left_h / 2) - int(self.PADDING_Y / 2)
        win_w = int(win_main_w / 3) - 2 * self.BORDER_W - self.PADDING_X
        win_y = self.BORDER_H + self.PADDING_Y
        win_x = win_main_w - self.BORDER_W - win_w - self.PADDING_X
        win = curses.newwin(win_h, win_w, win_y, win_x)
        self.win_list[WinId.RIGHT_TOP] = win

        # Bottom right window
        win_h = int(win_left_h / 2) - int(self.PADDING_Y / 2)
        win_w = int(win_main_w / 3) - 2 * self.BORDER_W - self.PADDING_X
        win_y = win_main_h - self.BORDER_H - win_h - self.PADDING_Y
        win_x = win_main_w - self.BORDER_W - win_w - self.PADDING_X
        win = curses.newwin(win_h, win_w, win_y, win_x)
        self.win_list[WinId.RIGHT_BOT] = win

        curses.init_pair(ColorPairId.RED_BLACK, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(ColorPairId.GREEN_BLACK, curses.COLOR_GREEN, curses.COLOR_BLACK)

    def add_log(self, msg: str) -> None:
        """
        Add log message

        Args:
            msg (str): Log message
        """

        win = self.win_list[WinId.RIGHT_BOT]
        msg += "\n"
        win.addstr(msg)
        win.refresh()

    def clear_log(self) -> None:
        """
        Clear log
        """

        win = self.win_list[WinId.RIGHT_BOT]
        win.clear()

    def display_choice_menu(self, name: str, msg: str, choice_list: List[str]) -> int:
        """
        Display choice menu

        Args:
            choice_list (List[str]): Choice list

        Returns:
            int: Selected choice index
        """

        choice_hl_idx: int = 0

        # Bottom right window
        win = self.win_list[WinId.RIGHT_BOT]

        win.clear()
        win.border()
        win.addstr(0, 2, f" {name} ", A_BOLD)
        win.addstr(2, 2, msg)

        while True:

            (win_y, win_x) = (4, 2)

            for choice in choice_list:

                choice_idx = choice_list.index(choice)
                disp_flag = A_NORMAL
                if choice_idx == choice_hl_idx:
                    disp_flag += A_STANDOUT
                win.addstr(win_y, win_x, choice, disp_flag)
                win_y += 1

            # Get key
            key = win.getkey()

            # Highlight previous field
            if key == "KEY_UP":
                choice_hl_idx -= 1
                if choice_hl_idx < 0:
                    choice_hl_idx = 0

            # Highlight next field
            elif key == "KEY_DOWN":
                choice_hl_idx += 1
                if choice_hl_idx >= len(choice_list):
                    choice_hl_idx = len(choice_list) - 1

            # Select highlighted choice
            elif key == "\n":
                break

            # Exit
            elif key == '\x1b':
                choice_hl_idx = -1
                break

        win.clear()
        win.refresh()

        return choice_hl_idx

class ItemDispCurses():
    """
    Curses item display
    """

    SEPARATOR = ""
    HEADER = ""
    MISSING = ""

    def __init__(self, disp: DispCurses) -> None:

        # Main display
        self.disp = disp

        self.field_nb = 0

        self.name = ""

    def raise_no_override(self, method: str = "") -> None:
        """
        Raise method not overriden exception

        Args:
            method_name (str, optional): Method name. Defaults to "".
        """

        raise NoOverrideError(
            base_class="ItemDispCurses",
            derived_class=type(self).__name__,
            method=method)

    def set_item(self, item: Union[Statement, Operation]):
        """
        Set item
        """

        self.raise_no_override("set_item")
        _ = item

    def get_item_field(self, field_idx: int) -> Tuple[str, str]:
        """
        Get item field
        """

        self.raise_no_override("get_item_field")
        _ = field_idx
        return ("", "")

    def set_item_field(self, field_idx: int, val_str: str) -> bool:
        """
        Set item field
        """

        self.raise_no_override("set_item_field")
        _ = field_idx
        _ = val_str
        return False

    def display_item_win(self, win: Window, field_hl_idx: int = 0) -> None:
        """
        Display item in window
        """

        (win_y, win_x) = (2, 2)

        for field_idx in range(self.field_nb):

            (name, value) = self.get_item_field(field_idx)

            disp_flag = A_NORMAL
            if field_idx == field_hl_idx:
                disp_flag += A_STANDOUT

            win.addstr(win_y, win_x, f"{name} : {value}", disp_flag)
            win_y += 1

        win_y += 1
        win.move(win_y, win_x)

        # win.refresh()

    def edit_item_field(self, win: Window, field_idx: int) -> bool:
        """
        Edit item field
        Print prompt to edit item field

        Args:
            win (Window): Window to use
            field_idx (int): Index of field to edit

        Returns:
            bool: Is item field edited
        """

        is_edited: bool = False

        (win_y, win_x) = win.getyx()

        # Field value edit prompt
        win.addstr(win_y, win_x, "Value : ")

        # Get field value input
        win.keypad(False)
        curses.echo()
        val_str = win.getstr().decode(encoding="utf-8")
        win.keypad(True)
        curses.noecho()

        # If field value input
        if val_str != "":

            # Set field value
            is_edited = self.set_item_field(field_idx, val_str)

        return is_edited

    def edit_item(self, force_iterate: bool = False) -> bool:
        """
        Edit item
        """

        is_edited: bool = False
        field_hl_idx: int = 0
        win = self.disp.win_list[WinId.RIGHT_BOT]

        win.clear()
        win.keypad(True)

        while True:

            self.display_item_win(win, field_hl_idx)
            (win_y, win_x) = win.getyx()

            win.clrtoeol()
            win.border()
            win.move(0, 2)
            win.addstr(f" {self.name} ", A_BOLD)

            win.move(win_y, win_x)

            if force_iterate:

                self.edit_item_field(win, field_hl_idx)
                field_hl_idx += 1
                if field_hl_idx >= self.field_nb:
                    break

            else:

                # Get key
                key = win.getkey()

                # Highlight previous field
                if key == "KEY_UP":
                    field_hl_idx -= 1
                    if field_hl_idx < 0:
                        field_hl_idx = 0

                # Highlight next field
                elif key == "KEY_DOWN":
                    field_hl_idx += 1
                    if field_hl_idx > self.field_nb:
                        field_hl_idx = self.field_nb

                # Edit highlighted field
                elif key == "\n":

                    is_edited_single = self.edit_item_field(win, field_hl_idx)
                    if is_edited_single:
                        is_edited = True

                # Exit
                elif key == '\x1b':
                    break

        win.clear()
        win.refresh()

        return is_edited

class ContainerDispCurses():
    """
    Curses container (account, statement) display
    """

    def __init__(self, disp: DispCurses, item_disp: ItemDispCurses) -> None:

        # Main display
        self.disp = disp

        # Item display
        self.item_disp = item_disp

        self.name = ""

        # Highlighted item
        self.item_hl: Union[Statement, Operation] = None

        # Selected item list
        self.item_sel_list: List[Union[Statement, Operation]] = []

        # Focused item index
        self.item_focus_idx: int = 0

    def raise_no_override(self, method: str = "") -> None:
        """
        Raise method not overriden exception

        Args:
            method_name (str, optional): Method name. Defaults to "".
        """

        raise NoOverrideError(
            base_class="ContainerDispCurses",
            derived_class=type(self).__name__,
            method=method)

    def get_container_item_list(self) -> List[Union[Statement, Operation]]:
        """
        Get container item list
        """

        self.raise_no_override("get_container_item_list")
        return []

    def edit_container_item(self, item: Union[Statement, Operation]) -> bool:
        """
        Edit container item
        """

        self.raise_no_override("edit_container_item")
        _ = item
        return False

    def browse_container_item(self, item) -> None:
        """
        Browse container item
        """

        self.raise_no_override("browse_container_item")
        _ = item

    def create_container_item(self) -> Union[Statement, Operation]:
        """
        Create container item
        """

        self.raise_no_override("create_container_item")
        return Any

    def add_container_item(self, item: Union[Statement, Operation]) -> None:
        """
        Add container item

        Args:
            item (Union[Statement, Operation]): Item
        """

        self.raise_no_override("add_container_item")
        _ = item

    def remove_container_item_list(self, item_list: List[Union[Statement, Operation]]) -> RetCode:
        """
        Remove item list
        """

        if len(item_list) == 0:
            # No item to remove
            return RetCode.OK

        msg = f"Remove {len(item_list)} items"

        choice_list = [
            "Cancel",
            "Remove"
        ]

        choice_idx = self.disp.display_choice_menu("REMOVE ITEMS", msg, choice_list)

        # Default : Cancel
        ret = RetCode.CANCEL
        if choice_idx == 1:
            # Remove items
            ret = RetCode.OK

        return ret

    def remove_container_item(self, item: Union[Statement, Operation]) -> None:
        """
        Remove cotnainer item

        Args:
            item (Union[Statement, Operation]): Item
        """

        self.raise_no_override("remove_container_item")
        _ = item

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
            item_list: List[Union[Statement, Operation]] = self.get_container_item_list()
            self.item_hl = item_list[0]

        # Remove items list
        for item in item_list:
            self.remove_container_item(item)

    def paste(self) -> None:
        """
        Paste item(s)
        """

        item_list = self.disp.item_list_clipboard.get()
        if item_list is None or len(item_list) == 0:
            return

        # Add item list
        for item in item_list:
            self.add_container_item(item)

    def save(self) -> None:
        """
        Save
        """

        self.raise_no_override("save")

    def exit(self) -> RetCode:
        """
        Exit
        """

        choice_list = [
            "Cancel",
            "Save and exit",
            "Exit discarding changes"
        ]

        choice_idx = self.disp.display_choice_menu("EXIT", "Unsaved changes", choice_list)

        # Default : Cancel
        ret = RetCode.CANCEL
        if choice_idx == 1:
            ret = RetCode.EXIT_SAVE
        elif choice_idx == 2:
            ret = RetCode.EXIT_NO_SAVE

        return ret

    def display_container_info(self) -> None:
        """
        Display container info
        """

        self.raise_no_override("display_container_info")

    def display_container_item_list(self, hl_changed: bool, focus_changed: bool) -> None:
        """
        Display list of items (statements or operations) in container

        Args:
            hl_changed (bool): Is highlighted item updated
            focus_changed (bool): Is focused item updated
        """

        item_list: List[Union[Statement, Operation]] = self.get_container_item_list()

        # Left window
        win = self.disp.win_list[WinId.LEFT]
        win_h: int = win.getmaxyx()[0]

        # Number of displayed items
        item_disp_nb: int = win_h - 4
        if len(item_list) < item_disp_nb:
            item_disp_nb = len(item_list)

        # If highlighted item updated
        if hl_changed:

            # Fix focus

            item_hl_idx = item_list.index(self.item_hl)

            if item_hl_idx < self.item_focus_idx:

                # Move focus up
                self.item_focus_idx -= 1
                if self.item_focus_idx < 0:
                    self.item_focus_idx = 0

            elif item_hl_idx > self.item_focus_idx + item_disp_nb - 1:

                # Move focus down
                self.item_focus_idx += 1
                if self.item_focus_idx > len(item_list) - item_disp_nb:
                    self.item_focus_idx = len(item_list) - item_disp_nb

        # Else, if focus updated
        elif focus_changed:

            # Fix focus

            if self.item_focus_idx < 0:
                self.item_focus_idx = 0
            elif self.item_focus_idx > len(item_list) - item_disp_nb:
                self.item_focus_idx = len(item_list) - item_disp_nb

            # Fix highlighted item

            item_hl_idx = item_list.index(self.item_hl)

            if item_hl_idx < self.item_focus_idx:

                # Highlight first displayed item
                item_hl_idx = self.item_focus_idx
                self.item_hl = item_list[item_hl_idx]

            elif item_hl_idx > self.item_focus_idx + item_disp_nb - 1:

                # Highlight last displayed item
                item_hl_idx = self.item_focus_idx + item_disp_nb - 1
                self.item_hl = item_list[item_hl_idx]

        (win_y, win_x) = (0, 0)

        # Item separator
        win.addstr(win_y, win_x, self.item_disp.SEPARATOR)
        win_y += 1

        # Item header
        win.addstr(win_y, win_x, self.item_disp.HEADER)
        win_y += 1

        # TODO merge to common case
        if len(item_list) == 0:
            win.addstr(win_y, win_x, self.item_disp.SEPARATOR)
            win_y += 1
            win.addstr(win_y, win_x, self.item_disp.SEPARATOR)
            win_y += 1
            win.refresh()
            return

        # Item separator or missing
        if self.item_focus_idx == 0:
            win.addstr(win_y, win_x, self.item_disp.SEPARATOR)
        else:
            win.addstr(win_y, win_x, self.item_disp.MISSING)
        win_y += 1

        # Item list
        for item_idx in range(self.item_focus_idx, self.item_focus_idx + item_disp_nb):

            if item_idx >= len(item_list):
                break

            item = item_list[item_idx]

            disp_flag = A_NORMAL
            if item == self.item_hl:
                disp_flag += A_STANDOUT
            if item in self.item_sel_list:
                disp_flag += A_BOLD

            self.item_disp.set_item(item)
            self.item_disp.display_item_line(win, win_y, win_x, disp_flag)
            # self.display_item_line(item, win, win_y, win_x, disp_flag)
            win_y += 1

        # Item separator or missing
        if item_idx == len(item_list) - 1:
            win.addstr(win_y, win_x, self.item_disp.SEPARATOR)
        else:
            win.addstr(win_y, win_x, self.item_disp.MISSING)
        win_y += 1

        if len(item_list) != 0:
            op_disp_ratio = item_disp_nb / len(item_list)

        # Slider
        (win_y, win_x) = (3, win.getyx()[1])
        for _ in range(0, int(self.item_focus_idx * op_disp_ratio)):
            win.addstr(win_y, win_x, " ")
            win_y += 1
        for _ in range(int(self.item_focus_idx * op_disp_ratio),
                       int((self.item_focus_idx + item_disp_nb) * op_disp_ratio)):
            win.addstr(win_y, win_x, " ", A_STANDOUT)
            win_y += 1
        for _ in range(int((self.item_focus_idx + item_disp_nb) * op_disp_ratio),
                       int((len(item_list)) * op_disp_ratio)):
            win.addstr(win_y, win_x, " ")
            win_y += 1

        win.refresh()

    def browse_container(self):
        """
        Browse container
        """

        # Init
        item_list: List[Union[Statement, Operation]] = self.get_container_item_list()
        self.item_focus_idx: int = 0
        self.item_hl = None
        if len(item_list) != 0:
            self.item_hl = item_list[0]
        self.item_sel_list = []

        # Main window
        win = self.disp.win_list[WinId.MAIN]
        win.clear()
        win.border()
        win.move(0, 2)
        win.addstr(f" {self.name} ", A_BOLD)
        win.refresh()

        self.display_container_info()
        self.display_container_item_list(False, False)

        while True:

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
                self.item_focus_idx -= 3
                focus_changed = True

            # Focus next item
            elif key == "KEY_NPAGE":
                if self.item_hl is None:
                    continue
                self.item_focus_idx += 3
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
                self.edit_container_item(self.item_hl)
                self.disp.win_list[WinId.LEFT].clear()

            # Open highlighted item
            elif key == "\n":
                self.browse_container_item(self.item_hl)
                self.disp.win_list[WinId.LEFT].clear()

            # Add new item
            elif key in ("KEY_IC", "+"):
                item = self.create_container_item()
                if item is not None:
                    self.add_container_item(item)
                self.disp.win_list[WinId.LEFT].clear()

            # Remove item(s)
            elif key in ("KEY_DC", "-"):

                ret = RetCode.CANCEL

                item_list = []
                if len(self.item_sel_list) != 0:
                    item_list = self.item_sel_list
                elif self.item_hl is not None:
                    item_list = [self.item_hl]

                if len(item_list) > 0:

                    ret = self.remove_container_item_list(item_list)
                    if ret == RetCode.OK:
                        self.item_sel_list.clear()
                        self.item_hl = None

                    self.disp.win_list[WinId.LEFT].clear()

            # Save
            elif key == "s":
                self.save()

            # Exit
            elif key == '\x1b':
                ret = self.exit()
                if ret == RetCode.OK:
                    break

            item_list = self.get_container_item_list()

            if self.item_hl is None:
                if len(item_list) != 0:
                    self.item_hl = item_list[0]

            self.display_container_info()
            self.display_container_item_list(hl_changed, focus_changed)

class AccountDispCurses(ContainerDispCurses):
    """
    Curses account display
    """

    def __init__(self, account: Account, disp: DispCurses) -> None:

        # Init container item display
        stat_disp = StatementDispCurses(disp)

        # Init container display
        ContainerDispCurses.__init__(self, disp, stat_disp)

        # Account
        self.account: Account = account

        self.name = "ACCOUNT"

    def get_container_item_list(self) -> List[Statement]:
        """
        Get account statement list
        """

        return self.account.stat_list

    def add_container_item(self, stat: Statement) -> None:
        """
        Add account statement
        """

        self.account.add_stat(stat)

    def display_container_info(self) -> None:
        """
        Display account info
        """

        # Top right window
        win = self.disp.win_list[WinId.RIGHT_TOP]

        win.clear()
        win.border()
        win.addstr(0, 2, " INFO ", A_BOLD)

        (win_y, win_x) = (2, 2)

        win.addstr(win_y, win_x, "status : ")
        if self.account.is_saved:
            win.addstr("Saved", curses.color_pair(ColorPairId.GREEN_BLACK))
        else:
            win.addstr("Unsaved", curses.color_pair(ColorPairId.RED_BLACK))
        win_y += 1

        win.addstr(win_y, win_x,
                   f"clipboard : {self.disp.item_list_clipboard.get_len()} operations")
        win_y += 1

        win.refresh()

    def edit_container_item(self, stat: Statement) -> None:
        """
        Edit account statement

        Args:
            stat (Statement): Statement
        """

        stat_disp = StatementDispCurses(self.disp, stat)
        is_edited = stat_disp.edit_item()
        if is_edited:
            self.account.is_saved = False

    def browse_container_item(self, stat: Statement) -> None:
        """
        Browse account statement

        Args:
            stat (Statement): Statement
        """

        stat_disp = StatementDispCurses(self.disp, stat)
        stat_disp.browse_container()

    def remove_container_item_list(self, stat_list: List[Statement]) -> RetCode:
        """
        Remove account statement list
        """

        ret = super().remove_container_item_list(stat_list)
        if ret == RetCode.CANCEL:
            return ret

        # Confirmed
        self.account.remove_stat_list(stat_list)
        return RetCode.OK

    def create_container_item(self) -> Statement:
        """
        Create account statement
        """

        # Init statement
        stat: Statement = Statement(datetime.now(), 0.0, 0.0)

        # Init statement display
        stat_disp = StatementDispCurses(self.disp, stat)

        # Set statement fields
        stat_disp.edit_item(force_iterate=True)

        # Export statement file
        stat.export_file()

        return stat

    def save(self) -> None:
        """
        Save account
        """

        self.account.export_file()

    def exit(self) -> RetCode:
        """
        Exit account browse
        """

        if self.account.is_saved:
            # Saved : Exit
            return RetCode.OK

        # Unsaved changes

        ret_super = super().exit()

        ret = RetCode.CANCEL
        if ret_super == RetCode.EXIT_SAVE:
            self.account.export_file()
            ret = RetCode.OK
        elif ret_super == RetCode.EXIT_NO_SAVE:
            ret = RetCode.OK

        return ret

class StatementDispCurses(ItemDispCurses, ContainerDispCurses):
    """
    Curses statement display
    """

    # Item separator
    SEPARATOR = "|"
    SEPARATOR += "-" + "-".ljust(LEN_NAME, "-") + "-|"
    SEPARATOR += "-" + "-".ljust(LEN_DATE, "-") + "-|"
    SEPARATOR += "-" + "-".ljust(LEN_AMOUNT, "-") + "-|"
    SEPARATOR += "-" + "-".ljust(LEN_AMOUNT, "-") + "-|"
    SEPARATOR += "-" + "-".ljust(LEN_AMOUNT, "-") + "-|"
    SEPARATOR += "-" + "-".ljust(LEN_AMOUNT, "-") + "-|"

    # Item header
    HEADER = "|"
    HEADER += " " + "name".ljust(LEN_DATE, " ") + " |"
    HEADER += " " + "date".ljust(LEN_DATE, " ") + " |"
    HEADER += " " + "start".ljust(LEN_AMOUNT, " ") + " |"
    HEADER += " " + "end".ljust(LEN_AMOUNT, " ") + " |"
    HEADER += " " + "diff".ljust(LEN_AMOUNT, " ") + " |"
    HEADER += " " + "error".ljust(LEN_AMOUNT, " ") + " |"

    # Item missing
    MISSING = "|"
    MISSING += " " + "...".ljust(LEN_NAME, " ") + " |"
    MISSING += " " + "...".ljust(LEN_DATE, " ") + " |"
    MISSING += " " + "...".ljust(LEN_AMOUNT, " ") + " |"
    MISSING += " " + "...".ljust(LEN_AMOUNT, " ") + " |"
    MISSING += " " + "...".ljust(LEN_AMOUNT, " ") + " |"

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
        win.addstr(self.stat.date.strftime(FMT_DATE).ljust(LEN_NAME), flag)
        win.addstr(" | ")
        win.addstr(self.stat.date.strftime(FMT_DATE).ljust(LEN_DATE), flag)
        win.addstr(" | ")
        win.addstr(str(self.stat.bal_start).ljust(LEN_AMOUNT), flag)
        win.addstr(" | ")
        win.addstr(str(self.stat.bal_end).ljust(LEN_AMOUNT), flag)
        win.addstr(" | ")
        bal_diff = round(self.stat.bal_end - self.stat.bal_start, 2)
        if bal_diff >= 0.0:
            win.addstr(str(bal_diff).ljust(LEN_AMOUNT),
                       curses.color_pair(ColorPairId.GREEN_BLACK))
        else:
            win.addstr(str(bal_diff).ljust(LEN_AMOUNT),
                       curses.color_pair(ColorPairId.RED_BLACK))
        win.addstr(" | ")
        bal_err = round(self.stat.bal_start + self.stat.op_sum - self.stat.bal_end, 2)
        if bal_err == 0.0:
            win.addstr(str(bal_err).ljust(LEN_AMOUNT),
                       curses.color_pair(ColorPairId.GREEN_BLACK))
        else:
            win.addstr(str(bal_err).ljust(LEN_AMOUNT),
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

class OperationDispCurses(ItemDispCurses):
    """
    Curses operation display
    """

    # Item separator
    SEPARATOR = "|"
    SEPARATOR += "-" + "-".ljust(LEN_DATE, "-") + "-|"
    SEPARATOR += "-" + "-".ljust(LEN_MODE, "-") + "-|"
    SEPARATOR += "-" + "-".ljust(LEN_TIER, "-") + "-|"
    SEPARATOR += "-" + "-".ljust(LEN_CAT, "-") + "-|"
    SEPARATOR += "-" + "-".ljust(LEN_DESC, "-") + "-|"
    SEPARATOR += "-" + "-".ljust(LEN_AMOUNT, "-") + "-|"

    # Item header
    HEADER = "|"
    HEADER += " " + "date".ljust(LEN_DATE, " ") + " |"
    HEADER += " " + "mode".ljust(LEN_MODE, " ") + " |"
    HEADER += " " + "tier".ljust(LEN_TIER, " ") + " |"
    HEADER += " " + "cat".ljust(LEN_CAT, " ") + " |"
    HEADER += " " + "desc".ljust(LEN_DESC, " ") + " |"
    HEADER += " " + "amount".ljust(LEN_AMOUNT, " ") + " |"

    # Item missing
    MISSING = "|"
    MISSING += " " + "...".ljust(LEN_DATE, ' ') + " |"
    MISSING += " " + "...".ljust(LEN_MODE, ' ') + " |"
    MISSING += " " + "...".ljust(LEN_TIER, ' ') + " |"
    MISSING += " " + "...".ljust(LEN_CAT, ' ') + " |"
    MISSING += " " + "...".ljust(LEN_DESC, ' ') + " |"
    MISSING += " " + "...".ljust(LEN_AMOUNT, ' ') + " |"

    def __init__(self, disp: DispCurses, operation: Operation = None) -> None:

        # Init item display
        ItemDispCurses.__init__(self, disp)

        # Operation
        self.operation: Operation = operation

        # Window
        self.win = disp.win_list[WinId.RIGHT_BOT]

        # Index of operation highlighted field
        self.op_field_hl_idx = 0

        self.field_nb = Operation.FieldIdx.LAST + 1

        self.name = "OPERATION"

    def set_item(self, operation: Operation):
        """
        Set operation
        """

        self.operation = operation

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
        win.addstr(self.operation.date.strftime(FMT_DATE)[:LEN_DATE].ljust(LEN_DATE), flag)
        win.addstr(" | ")
        win.addstr(self.operation.mode[:LEN_MODE].ljust(LEN_MODE), flag)
        win.addstr(" | ")
        win.addstr(self.operation.tier[:LEN_TIER].ljust(LEN_TIER), flag)
        win.addstr(" | ")
        win.addstr(self.operation.cat[:LEN_CAT].ljust(LEN_CAT), flag)
        win.addstr(" | ")
        win.addstr(self.operation.desc[:LEN_DESC].ljust(LEN_DESC), flag)
        win.addstr(" | ")
        win.addstr(str(self.operation.amount)[:LEN_AMOUNT].ljust(LEN_AMOUNT), flag)
        win.addstr(" |")

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
    #         if field_idx == self.op_field_hl_idx:
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
