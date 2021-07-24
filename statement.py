
import csv
import curses
from curses import *
from datetime import datetime

from utils import *
from operation import Operation

class Statement(object):

    # CSV index
    IDX_INVALID = -1
    IDX_DATE = 0
    IDX_BAL_START = 1
    IDX_BAL_END = 2

    SEP = "|"
    SEP += f"-{'-'.ljust(LEN_DATE, '-')}-|"
    SEP += f"-{'-'.ljust(LEN_TYPE, '-')}-|"
    SEP += f"-{'-'.ljust(LEN_TIER, '-')}-|"
    SEP += f"-{'-'.ljust(LEN_CAT, '-')}-|"
    SEP += f"-{'-'.ljust(LEN_DESC, '-')}-|"
    SEP += f"-{'-'.ljust(LEN_AMOUNT, '-')}-|"

    HEADER = "|"
    HEADER += f" {'date'.ljust(LEN_DATE, ' ')} |"
    HEADER += f" {'type'.ljust(LEN_TYPE, ' ')} |"
    HEADER += f" {'tier'.ljust(LEN_TIER, ' ')} |"
    HEADER += f" {'category'.ljust(LEN_CAT, ' ')} |"
    HEADER += f" {'description'.ljust(LEN_DESC, ' ')} |"
    HEADER += f" {'amount'.ljust(LEN_AMOUNT, ' ')} |"

    UNCOMPLETE = "|"
    UNCOMPLETE += f" {'...'.ljust(LEN_DATE, ' ')} |"
    UNCOMPLETE += f" {'...'.ljust(LEN_TYPE, ' ')} |"
    UNCOMPLETE += f" {'...'.ljust(LEN_TIER, ' ')} |"
    UNCOMPLETE += f" {'...'.ljust(LEN_CAT, ' ')} |"
    UNCOMPLETE += f" {'...'.ljust(LEN_DESC, ' ')} |"
    UNCOMPLETE += f" {'...'.ljust(LEN_AMOUNT, ' ')} |"

    def __init__(self, name: str, balStart: float, balEnd: float) -> None:

        self.name = name
        self.filePath = f"statements/{name}.csv"
        try:
            self.date = datetime.strptime(name, FMT_DATE)
        except:
            self.date = datetime.now()
        self.balStart = balStart
        self.balEnd = balEnd
        self.opSum = 0
        self.pOp:List[Operation] = list()

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
    def setField(self, idx, sVal) -> bool:

        bEdit = True

        if idx == self.IDX_DATE:
            try:
                self.date = datetime.strptime(sVal, FMT_DATE)
            except:
                bEdit = False
        elif idx == self.IDX_BAL_START:
            try:
                self.balStart = float(sVal)
            except:
                bEdit = False
        elif idx == self.IDX_BAL_END:
            try:
                self.balEnd = float(sVal)
            except:
                bEdit = False

        return bEdit

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

    # Edit statmenent
    def editStat(self, pWin: List[Window]) -> None:

        bDateEdit = False
        idxSel = 0

        while True:

            self.dispStat(pWin[WIN_IDX_INPUT], idxSel)

            key = pWin[WIN_IDX_INPUT].getkey()

            # Highlight previous field
            if key == "KEY_UP":
                idxSel = idxSel - 1
                if idxSel < self.IDX_DATE:
                    idxSel = self.IDX_BAL_END

            # Highlight next field
            elif key == "KEY_DOWN":
                idxSel = idxSel + 1
                if idxSel > self.IDX_BAL_END:
                    idxSel = self.IDX_DATE

            # Edit highlighted field
            elif key == "\n":

                pWin[WIN_IDX_INPUT].addstr("New value : ")
                pWin[WIN_IDX_INPUT].keypad(False)
                curses.echo()
                sVal = pWin[WIN_IDX_INPUT].getstr().decode(encoding="utf-8")
                pWin[WIN_IDX_INPUT].keypad(True)
                curses.noecho()

                if sVal != "":
                    bEdit = self.setField(idxSel, sVal)
                    # If date edited
                    if idxSel == self.IDX_DATE and bEdit == True:
                        bDateEdit = True

                # Highlight next field
                idxSel = idxSel + 1
                if idxSel > self.IDX_BAL_END:
                    idxSel = self.IDX_DATE

            # Exit
            elif key == '\x1b':
                break

        return bDateEdit

    # Display statement operations
    def dispOps(self, win: Window, opIdxFirst: int, opHl: Operation, pOpSel: list) -> None:

        (winH, _) = win.getmaxyx()
        nOpDisp = winH - 11
        if len(self.pOp) < nOpDisp:
            nOpDisp = len(self.pOp)

        win.clear()
        win.border()
        win.move(0, 2)
        win.addstr(" STATEMENT ", A_BOLD)

        (y, x) = (2, 2)
        win.addstr(y, x, self.SEP)
        # Get X at end of table
        xTableEnd = win.getyx()[1]
        y = y + 1
        win.addstr(y, x, "| ")
        win.addnstr('date'.ljust(LEN_DATE), LEN_DATE, A_BOLD)
        win.addstr(" | ")
        win.addnstr('type'.ljust(LEN_TYPE), LEN_TYPE, A_BOLD)
        win.addstr(" | ")
        win.addnstr('tier'.ljust(LEN_TIER), LEN_TIER, A_BOLD)
        win.addstr(" | ")
        win.addnstr('cat'.ljust(LEN_CAT), LEN_CAT, A_BOLD)
        win.addstr(" | ")
        win.addnstr('desc'.ljust(LEN_DESC), LEN_DESC, A_BOLD)
        win.addstr(" | ")
        win.addnstr('amount'.ljust(LEN_AMOUNT), LEN_AMOUNT, A_BOLD)
        win.addstr(" |")
        y = y + 1

        if opIdxFirst == 0:
            win.addstr(y, x, self.SEP)
        else:
            win.addstr(y, x, self.UNCOMPLETE)
        y = y + 1

        opIdx = opIdxFirst
        while opIdx < len(self.pOp) and opIdx < opIdxFirst + nOpDisp:

            op = self.pOp[opIdx]

            dispFlag = A_NORMAL
            if op == opHl:
                dispFlag += A_STANDOUT
            if op in pOpSel:
                dispFlag += A_BOLD

            win.addstr(y, x, "| ")
            win.addnstr(op.date.strftime(FMT_DATE).ljust(LEN_DATE), LEN_DATE, dispFlag)
            win.addstr(" | ")
            win.addnstr(op.type.ljust(LEN_TYPE), LEN_TYPE, dispFlag)
            win.addstr(" | ")
            win.addnstr(op.tier.ljust(LEN_TIER), LEN_TIER, dispFlag)
            win.addstr(" | ")
            win.addnstr(op.cat.ljust(LEN_CAT), LEN_CAT, dispFlag)
            win.addstr(" | ")
            win.addnstr(op.desc.ljust(LEN_DESC), LEN_DESC, dispFlag)
            win.addstr(" | ")
            win.addnstr(str(op.amount).ljust(LEN_AMOUNT), LEN_AMOUNT, dispFlag)
            win.addstr(" |")
            y = y + 1

            opIdx = opIdx + 1

        if opIdx == len(self.pOp):
            win.addstr(y, x, f"{self.SEP}\n")
        else:
            win.addstr(y, x, self.UNCOMPLETE)
        y = y + 1

        if len(self.pOp) != 0:
            # Slider
            (y2, x2) = (5, xTableEnd)
            for i in range(int(opIdxFirst * nOpDisp / len(self.pOp))):
                y2 = y2 + 1
            for i in range(int(nOpDisp * nOpDisp / len(self.pOp))):
                win.addstr(y2, x2, " ", A_STANDOUT)
                y2 = y2 + 1

        win.refresh()

    # Display fields
    def dispFields(self, win, fieldIdxHl) -> None:

        win.clear()
        win.border()
        win.move(0, 2)
        win.addstr(" INFO ", A_BOLD)

        (y, x) = (2, 2)
        dispFlag = A_NORMAL
        win.addstr(y, x, f"name : {self.name}")
        y = y + 1

        dispFlag = A_NORMAL
        if fieldIdxHl == self.IDX_DATE:
            dispFlag = A_STANDOUT
        win.addstr(y, x, f"date : {self.date.strftime(FMT_DATE)}", dispFlag)
        y = y + 1

        dispFlag = A_NORMAL
        if fieldIdxHl == self.IDX_BAL_START:
            dispFlag = A_STANDOUT
        win.addstr(y, x, f"start balance : {self.balStart}", dispFlag)
        y = y + 1

        dispFlag = A_NORMAL
        if fieldIdxHl == self.IDX_BAL_END:
            dispFlag = A_STANDOUT
        win.addstr(y, x, f"end balance : {self.balEnd}", dispFlag)
        y = y + 1

        win.addstr(y, x, f"actual end : {(self.balStart + self.opSum):.2f}")
        y = y + 1

        win.addstr(y, x, f"balance diff : {(self.balStart + self.opSum - self.balEnd):.2f}")
        y = y + 1

        win.refresh()

    # Edit statement operations
    def editOps(self, pWin: List[Window], statDst) -> None:

        (winMainH, _) = pWin[WIN_IDX_MAIN].getmaxyx()

        # Unsaved changes
        bUnsav : bool
        # Highlighted field index
        fieldIdxHl : int
        # Saved highlighted field index
        fieldIdxHlSav : int
        # First displayed operation index
        opIdxFirst : int
        # Highlighted operation
        opHl : Operation
        # Highlighted operation save
        opHlSav : Operation
        # Selected operations list
        pOpSel : List[Operation]

        # No unsaved changes
        bUnsav = False

        # No highlighted field
        fieldIdxHl = self.IDX_INVALID
        # Saved highlighted field is date
        fieldIdxHlSav = self.IDX_BAL_START

        # First displayed operations is first
        opIdxFirst = 0
        # Highlighted operation is first of statement
        if len(self.pOp) != 0:
            opHl = self.pOp[0]
        else:
            opHl = None
        # Save highlighted operation
        opHlSav = opHl

        # Init selected operations list
        pOpSel = list()

        while True:

            self.dispOps(pWin[WIN_IDX_MAIN], opIdxFirst, opHl, pOpSel)
            self.dispFields(pWin[WIN_IDX_INFO], fieldIdxHl)

            pWin[WIN_IDX_CMD].clear()
            pWin[WIN_IDX_CMD].border()
            pWin[WIN_IDX_CMD].addstr(0, 2, " COMMANDS ", A_BOLD)
            sCmd = "SPACE : (un)select, A/+ : add, D/DEL/-: delete, M : move, E/ENTER : edit/open"
            sCmd = sCmd + ", S : save, ESCAPE : exit"
            pWin[WIN_IDX_CMD].addstr(1, 2, sCmd)
            pWin[WIN_IDX_CMD].refresh()

            (y, x) = (2, 2)
            pWin[WIN_IDX_INFO].addstr(y, x, f"Destination statement : ")
            if statDst is not None:
                pWin[WIN_IDX_INFO].addstr(f"{statDst.name}")
            else:
                pWin[WIN_IDX_INFO].addstr(f"none")
            y = y + 1

            key = pWin[WIN_IDX_MAIN].getkey()

            # Move from operations to statement fields
            if key == "KEY_RIGHT":

                # Save highlighted operation
                opHlSav = opHl
                # No highlighted operation
                opHl = None
                # Backup highlighted field
                fieldIdxHl = fieldIdxHlSav

            # Move from statement fields to operations
            elif key == "KEY_LEFT":

                # Save highlighted field
                fieldIdxHlSav = fieldIdxHl
                # No highlighted field
                fieldIdxHl = self.IDX_INVALID
                # Backup highlighted operation
                opHl = opHlSav

            # Highlight previous
            elif key == "KEY_UP":

                # Operation
                if opHl is not None:

                    # Highlight previous operation
                    opHlIdx = self.pOp.index(opHl) - 1
                    if opHlIdx < 0:
                        opHlIdx = 0
                    opHl = self.pOp[opHlIdx]

                    # If out of display range
                    if opHlIdx < opIdxFirst:
                        # Previous page
                        opIdxFirst = opIdxFirst - 1
                        if opIdxFirst < 0:
                            opIdxFirst = 0

                # Statement field
                elif fieldIdxHl != self.IDX_INVALID:

                    fieldIdxHl = fieldIdxHl - 1
                    if fieldIdxHl < self.IDX_BAL_START:
                        fieldIdxHl = self.IDX_BAL_START

            # Highlight next operation
            elif key == "KEY_DOWN":

                # Operation
                if opHl is not None:

                    # Highlight next operation
                    opHlIdx = self.pOp.index(opHl) + 1
                    if opHlIdx >= len(self.pOp):
                        opHlIdx = len(self.pOp) - 1
                    opHl = self.pOp[opHlIdx]

                    # If out of display range
                    if opHlIdx - opIdxFirst >= winMainH - 11:
                        # Next page
                        opIdxFirst = opIdxFirst + 1
                        if opIdxFirst > len(self.pOp) - (winMainH - 11):
                            opIdxFirst = len(self.pOp) - (winMainH - 11)

                # Statement field
                elif fieldIdxHl != self.IDX_INVALID:

                    fieldIdxHl = fieldIdxHl + 1
                    if fieldIdxHl > self.IDX_BAL_END:
                        fieldIdxHl = self.IDX_BAL_END

            # Previous page
            elif key == "KEY_PPAGE":

                # Previous page
                opIdxFirst = opIdxFirst - 3
                if opIdxFirst < 0:
                    opIdxFirst = 0

                # If out of display range
                opHlIdx = self.pOp.index(opHl)
                if opHlIdx < opIdxFirst:
                    opHl = self.pOp[opIdxFirst]
                elif opHlIdx >= opIdxFirst + winMainH - 11:
                    opHl = self.pOp[opIdxFirst + winMainH - 11 - 1]

            # Next page
            elif key == "KEY_NPAGE":

                # Next page
                opIdxFirst = opIdxFirst + 3
                if opIdxFirst > len(self.pOp) - (winMainH - 11):
                    opIdxFirst = len(self.pOp) - (winMainH - 11)
                    if opIdxFirst < 0:
                        opIdxFirst = 0

                # If out of display range
                opHlIdx = self.pOp.index(opHl)
                if opHlIdx < opIdxFirst:
                    opHl = self.pOp[opIdxFirst]
                elif opHlIdx >= opIdxFirst + winMainH - 11:
                    opHl = self.pOp[opIdxFirst + winMainH - 11 - 1]

            # (Un)select operation
            elif key == " ":
                # If operation not selected
                if opHl not in pOpSel:
                    # Add operation to selected ones
                    pOpSel.append(opHl)
                # Else, operation selected
                else:
                    # Remove  operation to selected ones
                    pOpSel.remove(opHl)

            # Add operation
            elif key == "a" or key == "+":
                op = Operation(datetime.now(), "", "", "", "", 0.0)
                op.edit(pWin[WIN_IDX_INPUT])
                self.insertOp(op)
                bUnsav = True

            # Move selected operations
            elif key == "m":
                if statDst is None:
                    continue
                pWin[WIN_IDX_INPUT].clear()
                pWin[WIN_IDX_INPUT].border()
                pWin[WIN_IDX_INPUT].addstr(0, 2, " MOVE OPERATIONS ", A_BOLD)
                pWin[WIN_IDX_INPUT].addstr(2, 2, f"Move {len(pOpSel)} operations")
                pWin[WIN_IDX_INPUT].addstr(3, 2, f"To statement {statDst.name}")
                pWin[WIN_IDX_INPUT].addstr(5, 2, "Confirm ? (y/n) : ")
                cConfirm = pWin[WIN_IDX_INPUT].getch()
                if cConfirm != ord('y'):
                    continue
                # Move selected operations from current statement to last one
                self.moveOps(pOpSel, statDst)
                bUnsav = True
                # Clear select operations
                pOpSel.clear()

            # Delete selected operations
            elif key == "d" or key == "KEY_DC" or key == "-":

                pWin[WIN_IDX_INPUT].clear()
                pWin[WIN_IDX_INPUT].border()
                pWin[WIN_IDX_INPUT].addstr(0, 2, " DELETE OPERATIONS ", A_BOLD)
                pWin[WIN_IDX_INPUT].addstr(2, 2, f"Delete {len(pOpSel)} operations")
                pWin[WIN_IDX_INPUT].addstr(4, 2, "Confirm ? (y/n) : ")
                cConfirm = pWin[WIN_IDX_INPUT].getch()
                if cConfirm != ord('y'):
                    continue

                # Delete selected operations from current statement
                self.deleteOps(pOpSel)
                bUnsav = True

                # If highlighted operation in selected ones
                if opHl in pOpSel:
                    if len(self.pOp) >= 1:
                        opHl = self.pOp[0]
                    else:
                        opHl = None

                # Clear select operations
                pOpSel.clear()

            # (Edit/Open) highlited
            elif key == "e" or key == "\n":

                if opHl is not None:

                    (bEdit, bDateEdit) = opHl.edit(pWin[WIN_IDX_INPUT])
                    # If operation edited
                    if bEdit == True:
                        bUnsav = True
                        # If date edited
                        if bDateEdit == True:
                            # Remove and insert to update index
                            self.pOp.remove(opHl)
                            self.insertOp(opHl)

                elif fieldIdxHl != self.IDX_INVALID:

                    pWin[WIN_IDX_INPUT].clear()
                    pWin[WIN_IDX_INPUT].border()
                    pWin[WIN_IDX_INPUT].addstr(0, 2, " EDIT FIELD ", A_BOLD)
                    pWin[WIN_IDX_INPUT].addstr(2, 2, f"{self.getField(fieldIdxHl)}")
                    pWin[WIN_IDX_INPUT].addstr(4, 2, "New value : ")
                    pWin[WIN_IDX_INPUT].keypad(False)
                    curses.echo()
                    sVal = pWin[WIN_IDX_INPUT].getstr().decode(encoding="utf-8")
                    pWin[WIN_IDX_INPUT].keypad(True)
                    curses.noecho()

                    if sVal != "":
                        self.setField(fieldIdxHl, sVal)
                        bUnsav = True

            # Save
            elif key == "s":
                self.write()
                statDst.write()

            # Exit
            elif key == '\x1b':
                if bUnsav == True:
                    pWin[WIN_IDX_INPUT].clear()
                    pWin[WIN_IDX_INPUT].border()
                    pWin[WIN_IDX_INPUT].addstr(0, 2, " UNSAVED CHANGES ", A_BOLD)
                    pWin[WIN_IDX_INPUT].addstr(2, 2, "Save ? (y/n) : ")
                    cConfirm = pWin[WIN_IDX_INPUT].getch()
                    if cConfirm != ord('y'):
                        continue
                    self.write()
                    statDst.write()
                break

    # Insert operation
    def insertOp(self, op: Operation) -> int:

        # Find index
        idx = 0
        while idx < len(self.pOp) and op.date > self.pOp[idx].date:
            idx = idx + 1

        # Insert operation at dedicated index
        self.pOp.insert(idx, op)

        return OK

    # Move operations from source to destination statement
    def moveOps(self, pOp: list, statDst) -> None:

        # For each operation
        for op in pOp:
            # Insert operation in target statement
            statDst.insertOp(op)
            # Remove operation from statement
            self.pOp.remove(op)

    # Delete operations
    def deleteOps(self, pOp: list) -> None:

        # For each operation
        for op in pOp:
            # Remove operation from statement
            self.pOp.remove(op)
