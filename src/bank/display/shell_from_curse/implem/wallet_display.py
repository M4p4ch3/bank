"""
display/shell/implem/wallet
"""

from typing import (List)

from bank.display.shell.main import DisplayerMain
from bank.display.shell.container_display import DisplayerContainer
from bank.display.shell.implem.account_display import DisplayerAccount

from bank.internal.account import Account
from bank.internal.wallet import Wallet

from bank.utils.return_code import RetCode

class DisplayerWallet(DisplayerContainer):
    """
    Curses account display
    """

    def __init__(self, disp: DisplayerMain, wallet: Wallet = None) -> None:

        # Init container item display
        account_disp = DisplayerAccount(disp)

        # Init container display
        DisplayerContainer.__init__(self, disp, account_disp)

        # Wallet
        self.wallet: Wallet = wallet

        self.title = "WALLET"
        self.subtitle = "ACCOUNTS LIST"

    def get_container_item_list(self) -> List[Account]:
        """
        Get wallet account list
        """

        return self.wallet.account_list

    def add_container_item(self, item: Account) -> None:
        """
        Add wallet account
        """

        self.wallet.add_account(item)

    def display_container_info(self) -> None:
        """
        Display wallet info
        """

        print(" INFO ")

        print(f"balance : {self.wallet.get_bal():.2f}")

        print("status : ")
        if self.wallet.file_sync:
            print("Saved")
        else:
            print("Unsaved")

        print(f"clipboard : {self.disp.item_list_clipboard.get_len()} operations")

    def edit_container_item(self, item: Account) -> None:
        """
        Edit account statement

        Args:
            stat (Account): Account
        """

        account_disp = DisplayerAccount(self.disp, item)
        is_edited = account_disp.edit_item()
        if is_edited:
            self.wallet.file_sync = False

    def browse_container_item(self, item: Account) -> None:
        """
        Browse account statement

        Args:
            stat (Account): Account
        """

        account_disp = DisplayerAccount(self.disp, item)
        account_disp.browse_container()

    def remove_container_item_list(self, item_list: List[Account],
            force: bool = False) -> RetCode:
        """
        Remove account statement list
        """

        _ = force

        ret = super().remove_container_item_list(item_list)
        if ret == RetCode.CANCEL:
            return ret

        # Confirmed
        self.wallet.remove_stat_list(item_list)
        return RetCode.OK

    def create_container_item(self) -> Account:
        """
        Create wallet account
        """

        # Init account
        account: Account = Account(self.wallet.dir)

        # Init account display
        account_disp = DisplayerAccount(self.disp, account)

        # Set account fields
        account_disp.edit_item(force_iterate=True)

        # Export account file
        account.write_dir()

        return account

    def save(self) -> None:
        """
        Save account
        """

        self.wallet.write_dir()

    def exit(self) -> RetCode:
        """
        Exit account browse
        """

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
