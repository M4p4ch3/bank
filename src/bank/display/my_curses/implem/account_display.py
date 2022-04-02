"""
display/curses/implem/account
"""

import curses
from curses import A_BOLD
from datetime import datetime
from typing import (List)

from bank.display.my_curses.main import (ColorPairId, WinId, DisplayerMain)
from bank.display.my_curses.container_display import DisplayerContainer
from bank.display.my_curses.implem.statement_display import DisplayerStatement

from bank.internal.account import Account
from bank.internal.statement import Statement
from bank.utils.my_date import FMT_DATE

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

        stat_disp = DisplayerStatement(self.disp, stat)
        is_edited = stat_disp.edit_item()
        if is_edited:
            self.account.is_saved = False

    def browse_container_item(self, stat: Statement) -> None:
        """
        Browse account statement

        Args:
            stat (Statement): Statement
        """

        stat_disp = DisplayerStatement(self.disp, stat)
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
        parent_dir = self.account.dir
        identifier = self.account.stat_list[len(self.account.stat_list) - 1].identifier + 1
        name = datetime.now().strftime(FMT_DATE)
        date = datetime.now()
        bal_start = 0.0
        bal_end = 0.0
        stat: Statement = Statement(parent_dir, identifier, name, date, bal_start, bal_end)

        # Init statement display
        stat_disp = DisplayerStatement(self.disp, stat)

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
