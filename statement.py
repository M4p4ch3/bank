
import csv
import curses
from curses import *
from datetime import datetime
import time
from typing import List

from utils import *
from operation import Operation
import account

class Statement(object):

    # CSV index
    IDX_INVALID = -1
    IDX_DATE = 0
    IDX_BAL_START = 1
    IDX_BAL_END = 2



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

    def read(self) -> None:

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
            return

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

        file.close()

    # Write CSV file
    def write(self) -> int:

        # Open CSV file
        file = open(self.filePath, "w")
        fileCsv = csv.writer(file, delimiter=',', quotechar='"')

        # For each operation
        for op in self.pOp:

            # Create operation line
            opCsv = [op.date.strftime(FMT_DATE), op.type, op.tier,
                op.cat, op.desc, str(op.amount)]

            # Write operation line to CSV file
            fileCsv.writerow(opCsv)

        self.bUnsav = False

        file.close()

        return OK

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

    # Get attribute identified by field index
    def getField(self, idx) -> str:

        ret = ""
        if idx == self.IDX_DATE:
            ret = f"date : {self.date.strftime(FMT_DATE)}"
        elif idx == self.IDX_BAL_START:
            ret = f"start balance : {str(self.balStart)}"
        elif idx == self.IDX_BAL_END:
            ret = f"start balance : {str(self.balEnd)}"
        return ret

    # Set attribute identified by field index from string
    def setField(self, idx, sVal):

        if idx == self.IDX_DATE:
            try:
                self.date = datetime.strptime(sVal, FMT_DATE)
                self.bUnsav = True
            except:
                pass
        elif idx == self.IDX_BAL_START:
            try:
                self.balStart = float(sVal)
                self.bUnsav = True
            except:
                pass
        elif idx == self.IDX_BAL_END:
            try:
                self.balEnd = float(sVal)
                self.bUnsav = True
            except:
                pass

    # Display statement
    def dispStat(self, win, idxSel: int) -> None:

        win.clear()
        win.border()
        win.move(0, 2)
        win.addstr(" STATEMENT INFO ")

        (y, x) = (2, 2)
        for idx in range(self.IDX_BAL_END + 1):

            dispFlag = A_NORMAL
            if idx == idxSel:
                dispFlag = A_STANDOUT

            win.addstr(y, x, self.getField(idx), dispFlag)
            y = y + 1

        win.refresh()

    def save(self, win):

        self.write()
        self.bUnsav = False

    # # Edit statmenent
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

    # Display statement operations
    def dispOps(self, win, opIdxFirst: int, opHl: Operation, pOpSel: list) -> None:

        pass

    # Display fields
    def dispFields(self, win, fieldIdxHl) -> None:

        pass

    def addOp(self, pWin) -> None:

        op = Operation(datetime.now(), "", "", "", "", 0.0)

        op.editLin(pWin[WIN_IDX_INPUT])

        pWin[WIN_IDX_STATUS].clear()
        pWin[WIN_IDX_STATUS].border()
        pWin[WIN_IDX_STATUS].addstr(0, 2, " STATUS ", A_BOLD)
        pWin[WIN_IDX_STATUS].addstr(1, 2, "Insert operation")
        pWin[WIN_IDX_STATUS].refresh()

        self.insertOp(op)

        pWin[WIN_IDX_STATUS].addstr(1, 2, "Insert operation : OK")
        pWin[WIN_IDX_STATUS].refresh()

        time.sleep(1)

    # Insert operation
    def insertOp(self, op: Operation) -> int:

        # Find index
        idx = 0
        while idx < len(self.pOp) and op.date > self.pOp[idx].date:
            idx = idx + 1

        # Insert operation at dedicated index
        self.pOp.insert(idx, op)

        self.bUnsav = True

        return OK

    # Move operations from source to destination statement
    def moveOps(self, pOp : List[Operation], pWin) -> None:

        pWin[WIN_IDX_INPUT].clear()
        pWin[WIN_IDX_INPUT].border()
        pWin[WIN_IDX_INPUT].addstr(0, 2, " MOVE OPERATIONS ", A_BOLD)
        pWin[WIN_IDX_INPUT].addstr(2, 2, f"Destination statement : ")
        pWin[WIN_IDX_INPUT].addstr(3, 2, f"  Name (date) : ")
        curses.echo()
        sStatDstName = pWin[WIN_IDX_INPUT].getstr().decode(encoding="utf-8")
        curses.noecho()
        statDst = account.getStatByName(sStatDstName)
        if statDst is None:
            pWin[WIN_IDX_INPUT].addstr(4, 2, f"  Not found")
            pWin[WIN_IDX_INPUT].refresh()
            time.sleep(1)
            return

        pWin[WIN_IDX_INPUT].clear()
        pWin[WIN_IDX_INPUT].border()
        pWin[WIN_IDX_INPUT].addstr(0, 2, " MOVE OPERATIONS ", A_BOLD)
        pWin[WIN_IDX_INPUT].addstr(2, 2, f"Move {len(pOp)} operations")
        pWin[WIN_IDX_INPUT].addstr(3, 2, f"To statement {statDst.name}")
        pWin[WIN_IDX_INPUT].addstr(5, 2, "Confirm ? (y/n) : ")
        cConfirm = pWin[WIN_IDX_INPUT].getch()
        if cConfirm != ord('y'):
            return

        pWin[WIN_IDX_STATUS].clear()
        pWin[WIN_IDX_STATUS].border()
        pWin[WIN_IDX_STATUS].addstr(0, 2, " STATUS ", A_BOLD)
        pWin[WIN_IDX_STATUS].addstr(1, 2, "Move operations")
        pWin[WIN_IDX_STATUS].refresh()

        # Move selected operations from current to destination statement

        # For each operation
        for op in pOp:
            # Insert operation in target statement
            statDst.insertOp(op)
            # Remove operation from statement
            self.pOp.remove(op)

        self.bUnsav = True

        # Save current and destination statement
        self.save(pWin[WIN_IDX_STATUS])
        statDst.write()
        pWin[WIN_IDX_STATUS].addstr(1, 2, "Move operations : OK")
        pWin[WIN_IDX_STATUS].refresh()
        time.sleep(1)

    # Delete operations
    def deleteOps(self, pOp : List[Operation], pWin) -> None:

        pWin[WIN_IDX_INPUT].clear()
        pWin[WIN_IDX_INPUT].border()
        pWin[WIN_IDX_INPUT].addstr(0, 2, " DELETE OPERATIONS ", A_BOLD)
        pWin[WIN_IDX_INPUT].addstr(2, 2, f"Delete {len(pOp)} operations")
        pWin[WIN_IDX_INPUT].addstr(4, 2, "Confirm ? (y/n) : ")
        cConfirm = pWin[WIN_IDX_INPUT].getch()
        if cConfirm != ord('y'):
            return

        pWin[WIN_IDX_STATUS].clear()
        pWin[WIN_IDX_STATUS].border()
        pWin[WIN_IDX_STATUS].addstr(0, 2, " STATUS ", A_BOLD)
        pWin[WIN_IDX_STATUS].addstr(1, 2, "Delete operations")
        pWin[WIN_IDX_STATUS].refresh()

        # Delete selected operations from current statement

        # For each operation
        for op in pOp:
            # Remove operation from statement
            self.pOp.remove(op)

        self.bUnsav = True

        pWin[WIN_IDX_STATUS].addstr(1, 2, "Delete operations : OK")
        pWin[WIN_IDX_STATUS].refresh()
        time.sleep(1)

    def editFiel(self, fiedlIdx : int, win):

        win.clear()
        win.border()
        win.addstr(0, 2, " EDIT FIELD ", A_BOLD)
        win.addstr(2, 2, f"{self.getField(fiedlIdx)}")
        win.addstr(4, 2, "New value : ")
        win.keypad(False)
        curses.echo()
        sVal = win.getstr().decode(encoding="utf-8")
        win.keypad(True)
        curses.noecho()

        if sVal != "":
            self.setField(fiedlIdx, sVal)

    # Edit statement operations
    def editOps(self, pWin, account) -> None:

        pass