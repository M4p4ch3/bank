"""
Wallet, list of accounts
"""

import json
import logging
import os
import shutil
from typing import List

from bank.internal.account import Account

class Wallet():
    """
    Wallet, list of accounts
    """

    CSV_KEY_LIST = ["id", "name"]

    def __init__(self, parent_dir: str, id: str = "") -> None:

        self.logger = logging.getLogger("Wallet")

        self.parent_dir: str = parent_dir
        self.id: str = id
        self.name: str = self.id

        self.dir: str = self.parent_dir + "/wallet_" + self.name
        self.account_list: List[Account] = []
        self.file_sync: bool = True

        self.logger.debug("parent_dir = %s", self.parent_dir)
        self.logger.debug("id = %s", self.id)
        self.logger.debug("name = %s", self.name)
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
        ret += f"{indent_str}accounts : [\n"
        for stat in self.account_list:
            ret += f"{indent_str}    {{\n"
            ret += stat.get_str(indent + 2) + "\n"
            ret += f"{indent_str}    }}\n"
        ret += f"{indent_str}]"

        return ret

    def get_account(self, name: str) -> Account:
        """
        Get statement by date
        """

        for account in self.account_list:
            if account.name == name:
                return account

        return None

    def get_bal(self) -> float:
        """Get balance
        Sum of account balance"""

        balance: float = 0

        for account in self.account_list:
            balance += account.get_bal()

        return balance

    def set_id(self, id: str) -> None:
        self.id = id
        self.dir: str = self.parent_dir + "/account_" + self.id

    def set_name(self, name: str) -> None:
        self.name = name

    def _read_info(self) -> None:

        file_name: str = self.dir + "/info.json"

        if not os.path.exists(file_name):
            self.logger.debug("File %s does not exist", file_name)
            return

        self.logger.debug("Open %s for reading", file_name)
        with open(file_name, "r", encoding="utf8") as file:

            data = json.load(file)

            if "name" in data:
                self.name = data["name"]
                self.logger.info("name = %s", self.name)

    def _read_account_list(self) -> None:

        self.logger.debug("List dir %s", self.dir)
        for item in os.listdir(self.dir):

            if os.path.isdir(self.dir + "/" + item) and "account_" in item:
                account_name = item[len("account_"):]
                self.logger.debug("Found account %s", account_name)

                self.logger.debug("Init account %s", account_name)
                account = Account(self, self.dir, account_name)
                self.logger.debug("Account inited : %s", account)

                self.account_list.append(account)

    def read_dir(self) -> None:
        """
        Read from folder
        """

        if not os.path.isdir(self.dir):
            self.logger.debug("Folder %s does not exist", self.dir)
            return

        self.logger.debug("Read info")
        self._read_info()

        self.account_list.clear()
        self.logger.debug("Read account list")
        self._read_account_list()

        self.logger.debug("File sync")
        self.file_sync = True

    def _write_info(self) -> None:

        file_name: str = self.dir + "/info.json"
        self.logger.debug("Open %s for writing", file_name)
        with open(file_name, "w", encoding="utf8") as file:

            data = {
                "name" : self.name,
            }

            self.logger.debug("Dump JSON to %s", file_name)
            json.dump(data, file)

    def _write_account_list(self) -> None:

        self.logger.debug("List dir %s", self.dir)
        for item in os.listdir(self.dir):

            if os.path.isdir(self.dir + "/" + item) and "account_" in item:
                account_name = item[len("account_"):]
                self.logger.debug("Found account %s", account_name)

                # Should account dir be removed ?
                remove_account_dir: bool = True

                for account in self.account_list:
                    if account.name == account_name:
                        # Stat still in list, dont remove
                        remove_account_dir = False
                        break

                if remove_account_dir:
                    # Stat dir not in list anymore, remove
                    self.logger.debug("Remove dir %s", item)
                    shutil.rmtree(self.dir + "/" + item)

        for account in self.account_list:
            self.logger.debug("Write account %s to folder", account.name)
            account.write_dir()

    def write_dir(self) -> None:
        """
        Write to folder
        """

        if not os.path.isdir(self.dir):
            self.logger.debug("Create folder %s", self.dir)
            os.mkdir(self.dir)

        self.logger.debug("Write info")
        self._write_info()

        self.logger.debug("Write accounts list")
        self._write_account_list()

        self.logger.debug("File sync")
        self.file_sync = True

    def add_account(self, account: Account) -> None:
        """
        Add accounts
        """

        idx = 0
        while idx < len(self.account_list):
            idx = idx + 1

        self.account_list.insert(idx, account)

        self.file_sync = False

    def remove_stat(self, account: Account) -> None:
        """
        Remove account
        """

        if account not in self.account_list:
            return

        self.account_list.remove(account)

        self.file_sync = False
