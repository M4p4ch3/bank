
import csv
import curses
from curses import *
from datetime import datetime
import time
from typing import (List, Tuple)

from utils import *
from operation import Operation
import account

class Statement(object):

    # Field index
    IDX_INVALID = -1
    IDX_DATE = 0
    IDX_BAL_START = 1
    IDX_BAL_END = 2
    IDX_LAST = IDX_BAL_END

    def __init__(self, name: str, balStart: float, balEnd: float) -> None:

        self.name : str = name
        self.filePath : str = f"statements/{name}.csv"
        try:
            self.date : datetime= datetime.strptime(name, FMT_DATE)
        except:
            self.date : datetime = datetime.now()
        self.balStart : float = balStart
        self.balEnd : float = balEnd
        self.opSum : float = 0.0
        self.pOp : List[Operation] = list()
        self.bUnsav : bool = False

    def getStr(self, indent: int = 0) -> str:

        sIndent = ""
        for i in range(indent):
            sIndent += "    "

        ret = ""
        ret += f"{sIndent}date : {self.date.strftime(FMT_DATE)}\n"
        ret += f"{sIndent}balance : [{str(self.balStart)}, {str(self.balEnd)}]\n"
        ret += f"{sIndent}operations sum : {str(self.opSum)}\n"
        ret += f"{sIndent}balance diff : {str(self.opSum - self.balEnd)}\n"
        ret += f"{sIndent}operations : [\n"
        for op in self.pOp:
            ret += f"{sIndent}    {{\n"
            ret += op.getStr(indent + 2) + "\n"
            ret += f"{sIndent}    }}\n"
        ret += f"{sIndent}]"

    # Get field (name, value), identified by field index
    def getField(self, iField : int) -> Tuple[str, str]:

        ret = ("", "")
        if iField == self.IDX_DATE:
            ret = ("date", self.date.strftime(FMT_DATE))
        elif iField == self.IDX_BAL_START:
            ret = ("start balance", str(self.balStart))
        elif iField == self.IDX_BAL_END:
            ret = ("start balance", str(self.balEnd))
        return ret

    # Set field value, identified by field index, from string
    def setField(self, iField, sVal) -> int:

        if iField == self.IDX_DATE:
            try:
                self.date = datetime.strptime(sVal, FMT_DATE)
                self.bUnsav = True
            except:
                return ERROR
        elif iField == self.IDX_BAL_START:
            try:
                self.balStart = float(sVal)
                self.bUnsav = True
            except:
                return ERROR
        elif iField == self.IDX_BAL_END:
            try:
                self.balEnd = float(sVal)
                self.bUnsav = True
            except:
                return ERROR

        return OK

    def read(self) -> int:

        status : int = OK

        try:
            # Open CSV file
            file = open(self.filePath, "r")
            fileCsv = csv.reader(file)
        except FileNotFoundError:
            # File not found
            # Create new statement
            file = open(self.filePath, "w+")
            file.close()
            # Don't proceed with read
            return OK

        # For each operation line in statement CSV file
        for opLine in fileCsv:

            # Create operation
            opDate = datetime.strptime(opLine[Operation.IDX_DATE], FMT_DATE)
            op = Operation(opDate, opLine[Operation.IDX_TYPE], opLine[Operation.IDX_TIER],
                opLine[Operation.IDX_CAT], opLine[Operation.IDX_DESC],
                float(opLine[Operation.IDX_AMOUNT]))

            # Add operation to list
            self.pOp.append(op)

            # Update operations sum
            self.opSum = self.opSum + op.amount

        self.bUnsav = False

        file.close()

        return OK

    # Write CSV file
    def write(self) -> int:

        try:
            # Open CSV file
            file = open(self.filePath, "w")
        except:
            return ERROR

        fileCsv = csv.writer(file, delimiter=',', quotechar='"')

        # For each operation
        for op in self.pOp:

            # Create operation line
            opCsv = [op.date.strftime(FMT_DATE), op.type, op.tier,
                op.cat, op.desc, str(op.amount)]

            try:
                # Write operation line to CSV file
                fileCsv.writerow(opCsv)
            except:
                return ERROR

        self.bUnsav = False

        file.close()

        return OK

    def reset(self) -> int:

        status : int = OK

        # Clear operations list
        self.pOp.clear()
        # Reset operations sum
        self.opSum = 0.0

        status = self.read()
        if status != OK:
            return ERROR

        self.bUnsav = False

        return OK

    def save(self) -> int:

        status : int = OK

        status = self.write()
        if status != OK:
            return ERROR

        self.bUnsav = False

        return OK

    def insertOp(self, op: Operation) -> int:

        # Find index
        idx = 0
        while idx < len(self.pOp) and op.date > self.pOp[idx].date:
            idx = idx + 1

        # Insert operation at dedicated index
        self.pOp.insert(idx, op)

        self.bUnsav = True

        return OK

    def delOps(self, pOp : List[Operation]) -> None:

        # For each operation
        for op in pOp:
            # Remove operation from statement
            self.pOp.remove(op)

        self.bUnsav = True

    # def editStat(self, pWin: List[Window]) -> None:

    #     bDateEdit = False
    #     idxSel = 0

    #     while True:

    #         self.dispStat(pWin[WIN_IDX_INPUT], idxSel)

    #         key = pWin[WIN_IDX_INPUT].getkey()

    #         # Highlight previous field
    #         if key == "KEY_UP":
    #             idxSel = idxSel - 1
    #             if idxSel < self.IDX_DATE:
    #                 idxSel = self.IDX_BAL_END

    #         # Highlight next field
    #         elif key == "KEY_DOWN":
    #             idxSel = idxSel + 1
    #             if idxSel > self.IDX_BAL_END:
    #                 idxSel = self.IDX_DATE

    #         # Edit highlighted field
    #         elif key == "\n":

    #             pWin[WIN_IDX_INPUT].addstr("New value : ")
    #             pWin[WIN_IDX_INPUT].keypad(False)
    #             curses.echo()
    #             sVal = pWin[WIN_IDX_INPUT].getstr().decode(encoding="utf-8")
    #             pWin[WIN_IDX_INPUT].keypad(True)
    #             curses.noecho()

    #             if sVal != "":
    #                 bEdit = self.setField(idxSel, sVal)
    #                 # If date edited
    #                 if idxSel == self.IDX_DATE and bEdit == True:
    #                     bDateEdit = True

    #             # Highlight next field
    #             idxSel = idxSel + 1
    #             if idxSel > self.IDX_BAL_END:
    #                 idxSel = self.IDX_DATE

    #         # Exit
    #         elif key == '\x1b':
    #             break

    #     return bDateEdit

    # def editFiel(self, fiedlIdx : int, win):

    #     win.clear()
    #     win.border()
    #     win.addstr(0, 2, " EDIT FIELD ", A_BOLD)
    #     win.addstr(2, 2, f"{self.getField(fiedlIdx)}")
    #     win.addstr(4, 2, "New value : ")
    #     win.keypad(False)
    #     curses.echo()
    #     sVal = win.getstr().decode(encoding="utf-8")
    #     win.keypad(True)
    #     curses.noecho()

    #     if sVal != "":
    #         self.setField(fiedlIdx, sVal)
