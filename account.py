
import csv
from datetime import datetime
import curses
from curses import *

from utils import *
from statement import Statement

class Account(object):

    SEP = "|"
    SEP += f"-{'-'.ljust(LEN_NAME, '-')}-|"
    SEP += f"-{'-'.ljust(LEN_DATE, '-')}-|"
    SEP += f"-{'-'.ljust(LEN_AMOUNT, '-')}-|"
    SEP += f"-{'-'.ljust(LEN_AMOUNT, '-')}-|"

    HEADER = "|"
    HEADER += f" {'name'.ljust(LEN_NAME, ' ')} |"
    HEADER += f" {'date'.ljust(LEN_DATE, ' ')} |"
    HEADER += f" {'start'.ljust(LEN_AMOUNT, ' ')} |"
    HEADER += f" {'end'.ljust(LEN_AMOUNT, ' ')} |"

    UNCOMPLETE = "|"
    UNCOMPLETE += f" {'...'.ljust(LEN_NAME, ' ')} |"
    UNCOMPLETE += f" {'...'.ljust(LEN_DATE, ' ')} |"
    UNCOMPLETE += f" {'...'.ljust(LEN_AMOUNT, ' ')} |"
    UNCOMPLETE += f" {'...'.ljust(LEN_AMOUNT, ' ')} |"

    def __init__(self) -> None:

        self.filePath = "statements.csv"

        # Statements list
        self.pStat = list()

        # Open statements CSV file
        statsFile = open(self.filePath, "r")
        statsCsv = csv.reader(statsFile)

        # For each statement line
        for statLine in statsCsv:
            
            # Create and read statement
            stat = Statement(statLine[Statement.IDX_DATE],
                float(statLine[Statement.IDX_BAL_START]), float(statLine[Statement.IDX_BAL_END]))
            stat.read()

            # Add statement to statements list
            self.pStat.append(stat)

        statsFile.close()

    # Write to CSV file
    def write(self) -> int:

        # Open CSV file
        file = open(self.filePath, "w")
        csvFile = csv.writer(file, delimiter=',', quotechar='"')

        # For each statement
        for stat in self.pStat:

            # Create statement line
            statCsv = [stat.name, str(stat.balStart), str(stat.balEnd)]

            # Write statement line to CSV file
            csvFile.writerow(statCsv)

        file.close()

        return OK

    def getStr(self, indent: int = 0) -> str:

        sIndent = ""
        for i in range(indent):
            sIndent += "    "
            
        ret = ""
        ret += f"{sIndent}statements : [\n"
        for stat in self.pStat:
            ret += f"{sIndent}    {{\n"
            ret += stat.getStr(indent + 2) + "\n"
            ret += f"{sIndent}    }}\n"
        ret += f"{sIndent}]"

        return ret

    def dispStats(self, win: Window, iStatFirst: int, statHl: Statement, statSel: Statement) -> None:

        (hWin, _) = win.getmaxyx()
        nStatDisp = hWin - 11
        if len(self.pStat) < nStatDisp:
            nStatDisp = len(self.pStat)

        win.clear()
        win.border()
        win.move(0, 2)
        win.addstr(" STATEMENTS ", A_BOLD)

        (y, x) = (2, 2)
        win.addstr(y, x, f"{self.SEP}")
        # Get X at end of table
        xTableEnd = win.getyx()[1]
        y = y + 1
        win.addstr(y, x, f"| ")
        win.addstr(f"{'name'.ljust(LEN_NAME)}", A_BOLD)
        win.addstr(" | ")
        win.addstr(f"{'date'.ljust(LEN_DATE)}", A_BOLD)
        win.addstr(" | ")
        win.addstr(f"{'start'.ljust(LEN_AMOUNT)}", A_BOLD)
        win.addstr(" | ")
        win.addstr(f"{'end'.ljust(LEN_AMOUNT)}", A_BOLD)
        win.addstr(" |")
        y = y + 1

        if iStatFirst == 0:
            win.addstr(y, x, f"{self.SEP}")
        else:
            win.addstr(y, x, self.UNCOMPLETE)
        y = y + 1

        iStat = iStatFirst
        while iStat < len(self.pStat) and iStat < iStatFirst + nStatDisp:

            stat = self.pStat[iStat]

            dispFlag = A_NORMAL
            if stat == statHl:
                dispFlag += A_STANDOUT
            if stat == statSel:
                dispFlag += A_BOLD

            win.addstr(y, x, f"| ")
            win.addstr(f"{stat.name.ljust(LEN_NAME)}", dispFlag)
            win.addstr(" | ")
            win.addstr(f"{stat.date.strftime(FMT_DATE).ljust(LEN_DATE)}", dispFlag)
            win.addstr(" | ")
            win.addstr(f"{str(stat.balStart).ljust(LEN_AMOUNT)}", dispFlag)
            win.addstr(" | ")
            win.addstr(f"{str(stat.balEnd).ljust(LEN_AMOUNT)}", dispFlag)
            win.addstr(" |")
            y = y + 1

            iStat = iStat + 1

        if iStat == len(self.pStat):
            win.addstr(y, x, f"{self.SEP}")
        else:
            win.addstr(y, x, self.UNCOMPLETE)
        y = y + 1

        # Slider
        (y2, x2) = (5, xTableEnd)
        for i in range(int(iStatFirst * nStatDisp / len(self.pStat))):
            y2 = y2 + 1
        for i in range(int(nStatDisp * nStatDisp / len(self.pStat)) + 1):
            win.addstr(y2, x2, " ", A_STANDOUT)
            y2 = y2 + 1

        win.refresh()

    def editStats(self, pWin: List[Window]) -> None:

        (hWinMain, _) = pWin[WIN_IDX_MAIN].getmaxyx()

        # Index of first displayed statement
        iStatFirst = 0
        # Highlighted statement
        statHl: Statement = self.pStat[0]
        # Selected statement
        statSel: Statement = None

        while True:

            self.dispStats(pWin[WIN_IDX_MAIN], iStatFirst, statHl, statSel)

            pWin[WIN_IDX_CMD].clear()
            pWin[WIN_IDX_CMD].border()
            pWin[WIN_IDX_CMD].addstr(0, 2, " COMMANDS ", A_BOLD)
            sCmd = "S/SPACE : (un)select, A/+ : add, D/DEL/- : delete, E : edit, ENTER : open "
            pWin[WIN_IDX_CMD].addstr(1, 2, sCmd)
            pWin[WIN_IDX_CMD].refresh()

            key = pWin[WIN_IDX_MAIN].getkey()

            # Highlight previous statement
            if key == "KEY_UP":

                # Highlight previous statement
                iStatHl = self.pStat.index(statHl) - 1
                if iStatHl < 0:
                    iStatHl = 0
                statHl = self.pStat[iStatHl]

                # If out of display range
                if iStatHl < iStatFirst:
                    # Previous page
                    iStatFirst = iStatFirst - 1
                    if iStatFirst < 0:
                        iStatFirst = 0    

            # Highlight next statement
            if key == "KEY_DOWN":

                # Highlight next statement
                iStatHl = self.pStat.index(statHl) + 1
                if iStatHl >= len(self.pStat):
                    iStatHl = len(self.pStat) - 1
                statHl = self.pStat[iStatHl]

                # If out of display range
                if iStatHl - iStatFirst >= hWinMain - 11:
                    # Next page
                    iStatFirst = iStatFirst + 1
                    if iStatFirst > len(self.pStat) - (hWinMain - 11):
                        iStatFirst = len(self.pStat) - (hWinMain - 11)

            # Previous page
            elif key == "KEY_PPAGE":

                # Previous page
                iStatFirst = iStatFirst - 3
                if iStatFirst < 0:
                    iStatFirst = 0

                # If out of display range
                iStatHl = self.pStat.index(statHl)
                if iStatHl < iStatFirst:
                    statHl = self.pStat[iStatFirst]
                elif iStatHl >= iStatFirst + hWinMain - 11:
                    statHl = self.pStat[iStatFirst + hWinMain - 11 - 1]

            # Next page
            elif key == "KEY_NPAGE":

                # Next page
                iStatFirst = iStatFirst + 3
                if iStatFirst > len(self.pStat) - (hWinMain - 11):
                    iStatFirst = len(self.pStat) - (hWinMain - 11)
                    if iStatFirst < 0:
                        iStatFirst = 0

                # If out of display range
                iStatHl = self.pStat.index(statHl)
                if iStatHl < iStatFirst:
                    statHl = self.pStat[iStatFirst]
                elif iStatHl >= iStatFirst + hWinMain - 11:
                    statHl = self.pStat[iStatFirst + hWinMain - 11 - 1]

            # (Un)select statement
            elif key == "s" or key == " ":
                # If statement not selected
                if statHl != statSel:
                    # Select statement
                    statSel = statHl
                # Else, statement selected
                else:
                    # Unselect satement
                    statSel = None

            # Add statement
            elif key == "a" or key == "+":
                self.addStat(pWin[WIN_IDX_INPUT])

            # Delete selected operations
            elif key == "d" or key == "KEY_DC" or key == "-":

                pWin[WIN_IDX_INPUT].clear()
                pWin[WIN_IDX_INPUT].border()
                pWin[WIN_IDX_INPUT].addstr(0, 2, " DELETE STATEMENT ", A_BOLD)
                pWin[WIN_IDX_INPUT].addstr(2, 2, "Confirm ? (y/n) : ")
                cConfirm = pWin[WIN_IDX_INPUT].getch()
                if cConfirm != ord('y'):
                    continue

                # Delete highlighted statement
                self.pStat.remove(statHl)
                # Write
                self.write()
                # Reset highlighted statement
                statHl = self.pStat[0]

            # Edit statement
            elif key == "e":
                bDateEdit = statHl.editStat()
                # If date edited
                if bDateEdit == True:
                    # Remove and insert to update index
                    self.pStat.remove(statHl)
                    self.insertStat(statHl)
                # Write in any case
                self.write()

            # Open statement
            elif key == "\n":
                statHl.editOps(pWin, statSel)

            elif key == '\x1b':
                break

    # Insert statement
    def insertStat(self, stat: Statement) -> int:

        # Find index
        idx = 0
        while idx < len(self.pStat) and stat.date > self.pStat[idx].date:
            idx = idx + 1

        # Insert statement at dedicated index
        self.pStat.insert(idx, stat)

        return OK

    def addStat(self, win: Window) -> None:

        win.clear()
        win.border()
        win.move(0, 2)
        win.addstr(" ADD STATEMENT ", A_BOLD)

        (y, x) = (2, 2)
        win.addstr(y, x, "date : ")
        y = y + 1
        win.addstr(y, x, "start balance : ")
        y = y + 1
        win.addstr(y, x, "end balance   : ")
        y = y + 1

        win.keypad(False)
        curses.echo()

        (y, x) = (2, 2)

        bConvert = False
        while bConvert != True:
            win.move(y, x + len("date : "))
            sVal = win.getstr().decode(encoding="utf-8")
            try:
                date = datetime.strptime(sVal, FMT_DATE)
                bConvert = True
            except:
                pass

        y = y + 1

        bConvert = False
        while bConvert != True:
            win.move(y, x + len("start balance : "))
            sVal = win.getstr().decode(encoding="utf-8")
            try:
                balStart = float(sVal)
                bConvert = True
            except:
                pass

        y = y + 1

        bConvert = False
        while bConvert != True:
            win.move(y, x + len("end balance   : "))
            sVal = win.getstr().decode(encoding="utf-8")
            try:
                balEnd = float(sVal)
                bConvert = True
            except:
                pass

        y = y + 1

        win.keypad(True)
        curses.noecho()

        # Statement CSV file does not exit
        # Read will create it
        stat = Statement(date.strftime(FMT_DATE), balStart, balEnd)
        stat.read()

        # Append statement to statements list
        self.insertStat(stat)

        # Write statements list
        self.write()
