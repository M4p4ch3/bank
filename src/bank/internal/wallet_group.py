"""
WalletGroup, list of wallets
"""

import json
import logging
import os
import shutil
from typing import List

from bank.internal.wallet import Wallet

class WalletGroup():
    """
    WalletGroup, list of wallets
    """

    CSV_KEY_LIST = ["id", "name"]

    def __init__(self, dir: str) -> None:

        self.logger = logging.getLogger("WalletGroup")

        self.dir = dir
        self.wallet_list: List[Wallet] = []
        self.file_sync: bool = True

        self.logger.debug("dir = %s", self.dir)

        self.logger.debug("Read dir")
        self.read_dir()

    def get_str(self, indent: int = 0) -> str:
        """
        Get string representation
        """

        indent_str = ""
        for _ in range(indent):
            indent_str += "    "

        ret = ""
        ret += f"{indent_str}wallets : [\n"
        for wallet in self.wallet_list:
            ret += f"{indent_str}    {{\n"
            ret += wallet.get_str(indent + 2) + "\n"
            ret += f"{indent_str}    }}\n"
        ret += f"{indent_str}]"

        return ret

    def get_wallet(self, name: str) -> Wallet | None:
        for wallet in self.wallet_list:
            if wallet.name == name:
                return wallet

        return None

    def get_bal(self) -> float:
        balance: float = 0

        for wallet in self.wallet_list:
            balance += wallet.get_bal()

        return balance

    def _read_wallet_list(self) -> None:

        self.logger.debug("List dir %s", self.dir)
        for item in os.listdir(self.dir):

            if os.path.isdir(self.dir + "/" + item) and "wallet_" in item:
                wallet_id = item[len("wallet_"):]
                self.logger.debug("Found wallet %s", wallet_id)

                self.logger.debug("Init wallet %s", wallet_id)
                wallet = Wallet(self.dir, wallet_id)
                self.logger.debug("Wallet inited : %s", wallet)

                self.wallet_list.append(wallet)

        self.logger.info(f"Wallets lits : [{', '.join(wallet.name for wallet in self.wallet_list)}]")

    def read_dir(self) -> None:
        """
        Read from folder
        """

        if not os.path.isdir(self.dir):
            self.logger.debug("Folder %s does not exist", self.dir)
            return

        self.wallet_list.clear()
        self.logger.debug("Read wallet list")
        self._read_wallet_list()

        self.logger.debug("File sync")
        self.file_sync = True

    def _write_wallet_list(self) -> None:

        self.logger.debug("List dir %s", self.dir)
        for item in os.listdir(self.dir):

            if os.path.isdir(self.dir + "/" + item) and "wallet_" in item:
                wallet_name = item[len("wallet_"):]
                self.logger.debug("Found wallet %s", wallet_name)

                # Should wallet dir be removed ?
                remove_wallet_dir: bool = True

                for wallet in self.wallet_list:
                    if wallet.name == wallet_name:
                        # Stat still in list, dont remove
                        remove_wallet_dir = False
                        break

                if remove_wallet_dir:
                    # Stat dir not in list anymore, remove
                    self.logger.debug("Remove dir %s", item)
                    shutil.rmtree(self.dir + "/" + item)

        for wallet in self.wallet_list:
            self.logger.debug("Write wallet %s to folder", wallet.name)
            wallet.write_dir()

    def write_dir(self) -> None:
        """
        Write to folder
        """

        if not os.path.isdir(self.dir):
            self.logger.debug("Create folder %s", self.dir)
            os.mkdir(self.dir)

        self.logger.debug("Write wallets list")
        self._write_wallet_list()

        self.logger.debug("File sync")
        self.file_sync = True

    def add_wallet(self, wallet: Wallet) -> None:
        idx = 0
        while idx < len(self.wallet_list):
            idx = idx + 1

        self.wallet_list.insert(idx, wallet)

        self.file_sync = False

    def remove_stat(self, wallet: Wallet) -> None:
        if wallet not in self.wallet_list:
            return

        self.wallet_list.remove(wallet)

        self.file_sync = False
