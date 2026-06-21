
import curses
from curses import A_BOLD
import logging
from typing import (List)

from bank.display.my_curses.main import (ColorPairId, WinId, DisplayerMain)
from bank.display.my_curses.container_display import DisplayerContainer
from bank.display.my_curses.implem.wallet_display import DisplayerWallet

from bank.internal.wallet import Wallet
from bank.internal.wallet_group import WalletGroup

from bank.utils.return_code import RetCode

class DisplayerWalletGroup(DisplayerContainer):
    def __init__(self, disp: DisplayerMain, wallet_group: WalletGroup) -> None:
        self.logger = logging.getLogger("DisplayerWalletGroup")
        self.logger.error("test")
        print("test")

        # Init container item display
        wallet_disp = DisplayerWallet(disp)

        # Init container display
        DisplayerContainer.__init__(self, disp, wallet_disp)

        # Wallet
        self.wallet_group: WalletGroup = wallet_group
        self.logger.info(f"Wallets lits : [{', '.join(wallet.name for wallet in self.wallet_group.wallet_list)}]")
        print(f"Wallets lits : [{', '.join(wallet.name for wallet in self.wallet_group.wallet_list)}]")

        self.title = ""
        self.subtitle = "WALLETS LIST"

    def get_container_item_list(self) -> List[Wallet]:
        return self.wallet_group.wallet_list

    def add_container_item(self, item: Wallet) -> None:
        self.wallet_group.add_wallet(item)

    def display_container_info(self) -> None:
        # Top right window
        win = self.disp.win_list[WinId.RIGHT_TOP]

        win.clear()
        win.border()
        win.addstr(0, 2, " INFO ", A_BOLD)

        (win_y, win_x) = (2, 2)

        win.addstr(win_y, win_x, f"balance : {self.wallet_group.get_bal():.2f}")
        win_y += 1

        win.addstr(win_y, win_x, "status : ")
        if self.wallet_group.file_sync:
            win.addstr("Saved", curses.color_pair(ColorPairId.GREEN_BLACK))
        else:
            win.addstr("Unsaved", curses.color_pair(ColorPairId.RED_BLACK))
        win_y += 1

        win.addstr(win_y, win_x,
                   f"clipboard : {self.disp.item_list_clipboard.get_len()} operations")
        win_y += 1

        win.refresh()

    def edit_container_item(self, item: Wallet) -> None:
        wallet_disp = DisplayerWallet(self.disp, item)
        is_edited = wallet_disp.edit_item()
        if is_edited:
            self.wallet_group.file_sync = False

    def browse_container_item(self, item: Wallet) -> None:
        wallet_disp = DisplayerWallet(self.disp, item)
        wallet_disp.browse_container()

    def remove_container_item_list(self, item_list: List[Wallet],
            force: bool = False) -> RetCode:
        _ = force

        ret = super().remove_container_item_list(item_list)
        if ret == RetCode.CANCEL:
            return ret

        # Confirmed
        # ERA TODO fix
        # self.wallet_group.remove_stat_list(item_list)
        return RetCode.OK

    def create_container_item(self) -> Wallet:
        # Init wallet
        wallet: Wallet = Wallet(self.wallet_group.dir)

        # Init wallet display
        wallet_disp = DisplayerWallet(self.disp, wallet)

        # Set wallet fields
        wallet_disp.edit_item(force_iterate=True)

        # Export wallet file
        wallet.write_dir()

        return wallet

    def save(self) -> None:
        self.wallet_group.write_dir()

    def exit(self) -> RetCode:
        if self.wallet_group.file_sync:
            # Saved : Exit
            return RetCode.OK

        # Unsaved changes

        ret = super().exit()

        if ret == RetCode.EXIT_SAVE:
            self.wallet_group.write_dir()
            return RetCode.OK

        if ret == RetCode.EXIT_NO_SAVE:
            self.wallet_group.read_dir()
            return RetCode.OK

        return RetCode.CANCEL
