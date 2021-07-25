
from datetime import datetime
from typing import Tuple

from utils import *

class Operation(object):

    # Field index
    IDX_INVALID = -1
    IDX_DATE = 0
    IDX_TYPE = 1
    IDX_TIER = 2
    IDX_CAT = 3
    IDX_DESC = 4
    IDX_AMOUNT = 5
    IDX_LAST = IDX_AMOUNT

    def __init__(self, date : datetime, type : str,
        tier : str, cat : str, desc : str, amount : float) -> None:

        self.date : datetime = date
        self.type : str = type
        self.tier : str = tier
        self.cat : str = cat
        self.desc : str = desc
        self.amount : float = amount

    def getStr(self, indent : int = 0) -> str:

        sIndent = ""
        for i in range(indent):
            sIndent += "    "

        ret = ""
        ret += f"{sIndent}date   : {self.date.strftime(FMT_DATE)}\n"
        ret += f"{sIndent}type   : {self.type}\n"
        ret += f"{sIndent}tier   : {self.tier}\n"
        ret += f"{sIndent}cat    : {self.cat}\n"
        ret += f"{sIndent}desc   : {self.desc}\n"
        ret += f"{sIndent}amount : {self.amount}"

        return ret

    # Get field (name, value), identified by field index
    def getField(self, iField) -> Tuple[str, str]:

        ret = ("", "")

        if iField == self.IDX_DATE:
            ret = ("date", self.date.strftime(FMT_DATE))
        elif iField == self.IDX_TYPE:
            ret = ("type", self.type)
        elif iField == self.IDX_TIER:
            ret = ("tier", self.tier)
        elif iField == self.IDX_CAT:
            ret = ("cat", self.cat)
        elif iField == self.IDX_DESC:
            ret = ("desc", self.desc)
        elif iField == self.IDX_AMOUNT:
            ret = ("amount", str(self.amount))

        return ret

    # Set field value, identified by field index, from string
    def setField(self, iField, sVal) -> int:

        if iField == self.IDX_DATE:
            try:
                self.date = datetime.strptime(sVal, FMT_DATE)
            except:
                return ERROR
        elif iField == self.IDX_TYPE:
            self.type = sVal
        elif iField == self.IDX_TIER:
            self.tier = sVal
        elif iField == self.IDX_CAT:
            self.cat = sVal
        elif iField == self.IDX_DESC:
            self.desc = sVal
        elif iField == self.IDX_AMOUNT:
            try:
                self.amount = float(sVal)
            except:
                return ERROR

        return OK
