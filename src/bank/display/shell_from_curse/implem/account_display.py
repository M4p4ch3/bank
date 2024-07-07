"""
display/shell/implem/account
"""

from typing import (Any, List, Tuple)

from bank.display.shell.main import DisplayerMain
from bank.display.shell.item_display import DisplayerItem
from bank.display.shell.container_display import DisplayerContainer
from bank.display.shell.implem.statement_display import DisplayerStatement
from bank.display.shell.implem.main import (FieldLen, formart_trunc_padd, format_amount)

from bank.internal.account import Account
from bank.internal.statement import Statement

from bank.utils.return_code import RetCode
from bank.utils.my_date import FMT_DATE

class DisplayerAccount(DisplayerItem, DisplayerContainer):
    """
    Curses account display
    """

    # Item separator
    SEPARATOR = "|"
    SEPARATOR += "-" + "-".ljust(FieldLen.LEN_NAME, "-") + "-|"
    SEPARATOR += "-" + "-".ljust(FieldLen.LEN_DATE, "-") + "-|"
    SEPARATOR += "-" + "-".ljust(FieldLen.LEN_AMOUNT, "-") + "-|"

    # Item header
    HEADER = "|"
    HEADER += " " + "name".ljust(FieldLen.LEN_NAME, " ") + " |"
    HEADER += " " + "last updat".ljust(FieldLen.LEN_DATE, " ") + " |"
    HEADER += " " + "balance".ljust(FieldLen.LEN_AMOUNT, " ") + " |"

    # Item missing
    MISSING = "|"
    MISSING += " " + "...".ljust(FieldLen.LEN_NAME, " ") + " |"
    MISSING += " " + "...".ljust(FieldLen.LEN_DATE, " ") + " |"
    MISSING += " " + "...".ljust(FieldLen.LEN_AMOUNT, " ") + " |"

    def __init__(self, disp: DisplayerMain, account: Account = None) -> None:

        # Init self item display
        DisplayerItem.__init__(self, disp)

        # Init container item display
        stat_disp = DisplayerStatement(disp)

        # Init container display
        DisplayerContainer.__init__(self, disp, stat_disp)

        # Account
        self.account: Account = account

        self.title = "ACCOUNT"
        self.subtitle = "STATEMENTS LIST"

    def get_container_name(self) -> str:
        """
        Get account name
        """

        return self.account.name

    def set_item(self, item: Account) -> None:
        """
        Set account
        """

        self.account = item

    def get_item_field(self, field_idx: int) -> Tuple[str, str]:
        """
        Get field (name, value), identified by field index
        """

        ret = ("", "")
        if field_idx == Account.FieldIdx.NAME:
            ret = ("name", self.account.name)

        return ret

    def set_item_field(self, field_idx: int, val_str: str) -> bool:
        """
        Set field value, identified by field index, from string
        """

        is_edited = True

        if field_idx == Account.FieldIdx.NAME:
            self.account.set_name(val_str)

        if is_edited:
            self.account.file_sync = False

        return is_edited

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

        print("INFO")
        print(f"balance : {self.account.get_bal():.2f}")

        print("status : ")
        if self.account.file_sync:
            print("Saved")
        else:
            print("Unsaved")

        print(f"clipboard : {self.disp.item_list_clipboard.get_len()} operations")

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

        stat_last_date = self.account.get_last_stat_date()
        stat_last_date_str = ""
        if stat_last_date:
            stat_last_date_str = stat_last_date.strftime(FMT_DATE)

        stat_line = "| "
        stat_line += formart_trunc_padd(self.account.name, FieldLen.LEN_NAME)
        stat_line += " | "
        stat_line += formart_trunc_padd(stat_last_date_str, FieldLen.LEN_DATE)
        stat_line += " | "
        stat_line += format_amount(self.account.get_bal(), FieldLen.LEN_AMOUNT)

        win.addstr(win_y, win_x, stat_line, flag)

        print(" |", flag)

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
