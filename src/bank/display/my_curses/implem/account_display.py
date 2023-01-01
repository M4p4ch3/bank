"""
display/curses/implem/account
"""

import curses
from curses import A_BOLD
from typing import (List)

from bank.display.my_curses.main import (ColorPairId, WinId, DisplayerMain)
from bank.display.my_curses.container_display import DisplayerContainer
from bank.display.my_curses.implem.statement_display import DisplayerStatement

from bank.internal.account import Account
from bank.internal.statement import Statement

from bank.utils.return_code import RetCode

class DisplayerAccount(DisplayerContainer):
    """
    Curses account display
    """

    def __init__(self, account: Account, disp: DisplayerMain) -> None:

        # Init container item display
        stat_disp = DisplayerStatement(disp)

        # Init container display
        DisplayerContainer.__init__(self, disp, stat_disp)

        # Account
        self.account: Account = account

        self.title = "ACCOUNT"
        self.subtitle = "STATEMENTS LIST"

    def get_container_item_list(self) -> List[Statement]:
        """
        Get account statement list
        """

        return self.account.stat_list

    def add_container_item(self, item: Statement) -> None:
        """
        Add account statement
        """

        self.account.add_stat(item)

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
        if self.account.file_sync:
            win.addstr("Saved", curses.color_pair(ColorPairId.GREEN_BLACK))
        else:
            win.addstr("Unsaved", curses.color_pair(ColorPairId.RED_BLACK))
        win_y += 1

        win.addstr(win_y, win_x,
                   f"clipboard : {self.disp.item_list_clipboard.get_len()} operations")
        win_y += 1

        win.refresh()

    def edit_container_item(self, item: Statement) -> None:
        """
        Edit account statement

        Args:
            stat (Statement): Statement
        """

        stat_disp = DisplayerStatement(self.disp, item)
        is_edited = stat_disp.edit_item()
        if is_edited:
            self.account.file_sync = False

    def browse_container_item(self, item: Statement) -> None:
        """
        Browse account statement

        Args:
            stat (Statement): Statement
        """

        stat_disp = DisplayerStatement(self.disp, item)
        stat_disp.browse_container()

    def remove_container_item_list(self, item_list: List[Statement],
            force: bool = False) -> RetCode:
        """
        Remove account statement list
        """

        _ = force

        ret = super().remove_container_item_list(item_list)
        if ret == RetCode.CANCEL:
            return ret

        # Confirmed
        self.account.remove_stat_list(item_list)
        return RetCode.OK

    def create_container_item(self) -> Statement:
        """
        Create account statement
        """

        # Init statement
        stat: Statement = Statement(self.account.dir)

        # Init statement display
        stat_disp = DisplayerStatement(self.disp, stat)

        # Set statement fields
        stat_disp.edit_item(force_iterate=True)

        # Export statement file
        stat.write_dir()

        return stat

    def save(self) -> None:
        """
        Save account
        """

        self.account.write_dir()

    def exit(self) -> RetCode:
        """
        Exit account browse
        """

        if self.account.file_sync:
            # Saved : Exit
            return RetCode.OK

        # Unsaved changes

        ret = super().exit()

        if ret == RetCode.EXIT_SAVE:
            self.account.write_dir()
            return RetCode.OK

        if ret == RetCode.EXIT_NO_SAVE:
            self.account.read_dir()
            return RetCode.OK

        return RetCode.CANCEL
