
from datetime import datetime
import curses
from curses import *

from utils import *

class Operation(object):

    # CSV index
    IDX_DATE = 0
    IDX_TYPE = 1
    IDX_TIER = 2
    IDX_CAT = 3
    IDX_DESC = 4
    IDX_AMOUNT = 5

    def __init__(self, date: datetime, type: str,
        tier: str, cat: str, desc: str, amount: float) -> None:

        self.date = date
        self.type = type
        self.tier = tier
        self.cat = cat
        self.desc = desc
        self.amount = amount
        self.bSel = 0

    def getStr(self, indent: int = 0) -> str:

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

    # Get attribute identified by field index
    def getField(self, idx) -> str:

        ret = ""
        if idx == self.IDX_DATE:
            ret = f"date : {self.date.strftime(FMT_DATE)}"
        elif idx == self.IDX_TYPE:
            ret = f"type : {self.type}"
        elif idx == self.IDX_TIER:
            ret = f"tier : {self.tier}"
        elif idx == self.IDX_CAT:
            ret = f"cat : {self.cat}"
        elif idx == self.IDX_DESC:
            ret = f"desc : {self.desc}"
        elif idx == self.IDX_AMOUNT:
            ret = f"amount : {str(self.amount)}"
        return ret

    # Set attribute identified by field index from string
    def setField(self, idx, sVal) -> bool:

        bEdit = True

        if idx == self.IDX_DATE:
            try:
                self.date = datetime.strptime(sVal, FMT_DATE)
            except:
                bEdit = False
        elif idx == self.IDX_TYPE:
            self.type = sVal
        elif idx == self.IDX_TIER:
            self.tier = sVal
        elif idx == self.IDX_CAT:
            self.cat = sVal
        elif idx == self.IDX_DESC:
            self.desc = sVal
        elif idx == self.IDX_AMOUNT:
            try:
                self.amount = float(sVal)
            except:
                bEdit = False
        
        return bEdit

    def disp(self, win, idxSel: int) -> None:

        win.clear()
        win.border()
        win.move(0, 2)
        win.addstr(" OPERATION ", A_BOLD)

        (y, x) = (2, 2)
        for idx in range(self.IDX_AMOUNT + 1):

            dispFlag = A_NORMAL
            if idx == idxSel:
                dispFlag = A_STANDOUT

            win.addstr(y, x, self.getField(idx), dispFlag)
            y = y + 1

        y = y + 1
        win.addstr(y, x, "")

        win.refresh()

    def edit(self, win: Window) -> bool:

        bDateEdit = False
        idxSel = 0

        while True:

            self.disp(win, idxSel)
            (y, x) = (win.getyx()[0], 2)

            key = win.getkey()

            # Highlight previous field
            if key == "KEY_UP":
                idxSel = idxSel - 1
                if idxSel < self.IDX_DATE:
                    idxSel = self.IDX_AMOUNT

            # Highlight next field
            elif key == "KEY_DOWN":
                idxSel = idxSel + 1
                if idxSel > self.IDX_AMOUNT:
                    idxSel = self.IDX_DATE

            # Edit highlighted field
            elif key == "\n":

                win.addstr(y, x, "New value : ")
                win.keypad(False)
                curses.echo()
                sVal = win.getstr().decode(encoding="utf-8")
                win.keypad(True)
                curses.noecho()

                if sVal != "":
                    bEdit = self.setField(idxSel, sVal)
                    # If date edited
                    if idxSel == self.IDX_DATE and bEdit == True:
                        bDateEdit = True

                # Highlight next field
                idxSel = idxSel + 1
                if idxSel > self.IDX_AMOUNT:
                    idxSel = self.IDX_DATE

            # Exit
            elif key == '\x1b':
                break

        return bDateEdit
