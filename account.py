
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

    def dispStats(self, win: Window, statHl: Statement, statSel: Statement) -> None:

        win.clear()
        win.border()
        win.move(0, 2)
        win.addstr(" STATEMENTS ", A_BOLD)

        (y, x) = (2, 2)
        win.addstr(y, x, f"{self.SEP}")
        y = y + 1
        win.addstr(y, x, f"{self.HEADER}")
        y = y + 1
        win.addstr(y, x, f"{self.SEP}")
        y = y + 1

        for stat in self.pStat:

            dispFlag = A_NORMAL
            if stat == statHl:
                dispFlag += A_STANDOUT
            if stat == statSel:
                dispFlag += A_BOLD

            win.addstr(y, x, f"|"
                f" {stat.name.ljust(LEN_NAME)} |"
                f" {stat.date.strftime(FMT_DATE).ljust(LEN_DATE)} |"
                f" {str(stat.balStart).ljust(LEN_AMOUNT)} |"
                f" {str(stat.balEnd).ljust(LEN_AMOUNT)} |",
                dispFlag)
            y = y + 1

        win.addstr(y, x, f"{self.SEP}")
        y = y + 1

        win.refresh()

    def editStats(self, pWin: List[Window]) -> None:

        statHl = self.pStat[0]
        statSel = None

        while True:

            self.dispStats(pWin[WIN_IDX_MAIN], statHl, statSel)

            pWin[WIN_IDX_CMD].clear()
            pWin[WIN_IDX_CMD].border()
            pWin[WIN_IDX_CMD].addstr(0, 2, " COMMANDS ", A_BOLD)
            sCmd = " s : (un)select, a : add, d : delete, e : edit, ENTER : open "
            pWin[WIN_IDX_CMD].addstr(1, 2, sCmd)
            pWin[WIN_IDX_CMD].refresh()

            key = pWin[WIN_IDX_MAIN].getkey()

            # Highlight previous statement
            if key == "KEY_UP":
                idx = self.pStat.index(statHl) - 1
                if idx < 0:
                    statHl = self.pStat[len(self.pStat) - 1]
                else:
                    statHl = self.pStat[idx]

            # Highlight next statement
            if key == "KEY_DOWN":
                idx = self.pStat.index(statHl) + 1
                if idx >= len(self.pStat):
                    statHl = self.pStat[0]
                else:
                    statHl = self.pStat[idx]

            # (Un)select statement
            elif key == "s":
                # If statement not selected
                if statHl != statSel:
                    # Select statement
                    statSel = statHl
                # Else, statement selected
                else:
                    # Unselect satement
                    statSel = None

            # Add statement
            elif key == "a":
                self.addStat(pWin[WIN_IDX_INPUT])

            # Delete selected operations
            elif key == "d":

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
