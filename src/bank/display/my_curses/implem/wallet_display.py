"""
display/curses/implem/wallet
"""

import curses
from curses import A_BOLD
from typing import (Any, List, Tuple)

from bank.display.my_curses.main import (ColorPairId, WinId, DisplayerMain)
from bank.display.my_curses.item_display import DisplayerItem
from bank.display.my_curses.container_display import DisplayerContainer
from bank.display.my_curses.implem.account_display import DisplayerAccount
from bank.display.my_curses.implem.main import (FieldLen, formart_trunc_padd, format_amount)

from bank.internal.account import Account
from bank.internal.wallet import Wallet

from bank.utils.return_code import RetCode
from bank.utils.my_date import FMT_DATE

class DisplayerWallet(DisplayerItem, DisplayerContainer):
    """
    Curses wallet display
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

    def __init__(self, disp: DisplayerMain, wallet: Wallet = None) -> None:

        # Init self item display
        DisplayerItem.__init__(self, disp)

        # Init container item display
        account_disp = DisplayerAccount(disp)

        # Init container display
        DisplayerContainer.__init__(self, disp, account_disp)

        # Wallet
        self.wallet: Wallet = wallet

        self.field_nb = Wallet.FieldIdx.LAST + 1

        self.title = "WALLET"
        self.subtitle = "ACCOUNTS LIST"

    def get_container_name(self) -> str:
        return self.wallet.name

    def set_item(self, item: Wallet) -> None:
        self.wallet = item

    def get_item_field(self, field_idx: int) -> Tuple[str, str]:
        ret = ("", "")
        if field_idx == Wallet.FieldIdx.ID:
            ret = ("id", self.wallet.id)
        elif field_idx == Wallet.FieldIdx.NAME:
            ret = ("name", self.wallet.name)
        return ret

    def set_item_field(self, field_idx: int, val_str: str) -> bool:
        is_edited = True

        if field_idx == Wallet.FieldIdx.ID:
            self.wallet.set_id(val_str)
        elif field_idx == Wallet.FieldIdx.NAME:
            self.wallet.set_name(val_str)

        if is_edited:
            self.wallet.file_sync = False

        return is_edited

    def get_container_item_list(self) -> List[Account]:
        return self.wallet.account_list

    def add_container_item(self, item: Account) -> None:
        self.wallet.add_account(item)

    def display_container_info(self) -> None:
        # Top right window
        win = self.disp.win_list[WinId.RIGHT_TOP]

        win.clear()
        win.border()
        win.addstr(0, 2, " INFO ", A_BOLD)

        (win_y, win_x) = (2, 2)

        win.addstr(win_y, win_x, f"balance : {self.wallet.get_bal():.2f}")
        win_y += 1

        win.addstr(win_y, win_x, "status : ")
        if self.wallet.file_sync:
            win.addstr("Saved", curses.color_pair(ColorPairId.GREEN_BLACK))
        else:
            win.addstr("Unsaved", curses.color_pair(ColorPairId.RED_BLACK))
        win_y += 1

        win.addstr(win_y, win_x,
                   f"clipboard : {self.disp.item_list_clipboard.get_len()} operations")
        win_y += 1

        win.refresh()

    def edit_container_item(self, item: Account) -> None:
        account_disp = DisplayerAccount(self.disp, item)
        is_edited = account_disp.edit_item()
        if is_edited:
            self.wallet.file_sync = False

    def browse_container_item(self, item: Account) -> None:
        account_disp = DisplayerAccount(self.disp, item)
        account_disp.browse_container()

    def remove_container_item_list(self, item_list: List[Account],
            force: bool = False) -> RetCode:
        _ = force

        ret = super().remove_container_item_list(item_list)
        if ret == RetCode.CANCEL:
            return ret

        # Confirmed
        # ERA TODO fix
        # self.wallet.remove_stat_list(item_list)
        return RetCode.OK

    def create_container_item(self) -> Account:
        # Init account
        account: Account = Account(self.wallet, self.wallet.dir)

        # Init account display
        account_disp = DisplayerAccount(self.disp, account)

        # Set account fields
        account_disp.edit_item(force_iterate=True)

        # Export account file
        account.write_dir()

        return account

    def display_item_line(self, win: Any,
                          win_y: int, win_x: int, flag) -> None:
        account_last_date = self.wallet.get_last_account_date()
        account_last_date_str = ""
        if account_last_date:
            account_last_date_str = account_last_date.strftime(FMT_DATE)

        if not self.wallet:
            return

        stat_line = "| "
        stat_line += formart_trunc_padd(self.wallet.name, FieldLen.LEN_NAME)
        stat_line += " | "
        stat_line += formart_trunc_padd(account_last_date_str, FieldLen.LEN_DATE)
        stat_line += " | "
        stat_line += format_amount(self.wallet.get_bal(), FieldLen.LEN_AMOUNT)

        win.addstr(win_y, win_x, stat_line, flag)

        win.addstr(" |", flag)

    def save(self) -> None:
        self.wallet.write_dir()

    def exit(self) -> RetCode:
        if self.wallet.file_sync:
            # Saved : Exit
            return RetCode.OK

        # Unsaved changes

        ret = super().exit()

        if ret == RetCode.EXIT_SAVE:
            self.wallet.write_dir()
            return RetCode.OK

        if ret == RetCode.EXIT_NO_SAVE:
            self.wallet.read_dir()
            return RetCode.OK

        return RetCode.CANCEL
