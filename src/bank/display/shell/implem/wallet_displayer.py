
from bank.display.shell.main_displayer import MainDisplayer
from bank.display.shell.container_displayer import ContainerDisplayer

from bank.internal.wallet import Wallet

class WalletDisplayer(ContainerDisplayer):

    def __init__(self, disp: MainDisplayer, wallet : Wallet) -> None:
        super().__init__(disp)
        self.wallet = wallet

    def show(self):
        print(f"{self.wallet.name}")

    def list(self):
        for account in self.wallet.account_list:
            print(f"{account.name}")

    def prompt(self):
        input_str = input(f"{self.wallet.name} > ")
        return input_str
