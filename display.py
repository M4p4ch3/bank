
import curses
from curses import *
from datetime import datetime
import sys
import time
from typing import (TYPE_CHECKING, List, Tuple)

from utils import *
from account import Account
from statement import Statement
from operation import Operation

if TYPE_CHECKING:
    from _curses import _CursesWindow
    Window = _CursesWindow
else:
    from typing import Any
    Window = Any

class DisplayCurses(object):

    # Color pair ID
    COLOR_PAIR_ID_RED_BLACK = 1
    COLOR_PAIR_ID_GREEN_BLACK = 2

    # Window ID
    WIN_ID_MAIN = 0
    WIN_ID_INFO = 1
    WIN_ID_INPUT = 2
    WIN_ID_CMD = 3
    WIN_ID_STATUS = 4
    WIN_ID_LAST = WIN_ID_STATUS

    # Statement separator
    SEP_STAT = "|"
    SEP_STAT += "-" + "-".ljust(LEN_NAME, "-") + "-|"
    SEP_STAT += "-" + "-".ljust(LEN_DATE, "-") + "-|"
    SEP_STAT += "-" + "-".ljust(LEN_AMOUNT, "-") + "-|"
    SEP_STAT += "-" + "-".ljust(LEN_AMOUNT, "-") + "-|"
    SEP_STAT += "-" + "-".ljust(LEN_AMOUNT, "-") + "-|"
    SEP_STAT += "-" + "-".ljust(LEN_AMOUNT, "-") + "-|"

    # # Statement header
    # HEADER_STAT = "|"
    # HEADER_STAT += " " + "name".ljust(LEN_NAME, " ") + " |"
    # HEADER_STAT += " " + "date".ljust(LEN_DATE, " ") + " |"
    # HEADER_STAT += " " + "start".ljust(LEN_AMOUNT, " ") + " |"
    # HEADER_STAT += " " + "end".ljust(LEN_AMOUNT, " ") + " |"
    # HEADER_STAT += " " + "diff".ljust(LEN_AMOUNT, " ") + " |"
    # HEADER_STAT += " " + "err".ljust(LEN_AMOUNT, " ") + " |"

    # Statement missing
    MISS_STAT = "|"
    MISS_STAT += " " + "...".ljust(LEN_NAME, " ") + " |"
    MISS_STAT += " " + "...".ljust(LEN_DATE, " ") + " |"
    MISS_STAT += " " + "...".ljust(LEN_AMOUNT, " ") + " |"
    MISS_STAT += " " + "...".ljust(LEN_AMOUNT, " ") + " |"
    MISS_STAT += " " + "...".ljust(LEN_AMOUNT, " ") + " |"

    # Operation separator
    SEP_OP = "|"
    SEP_OP += "-" + "-".ljust(LEN_DATE, "-") + "-|"
    SEP_OP += "-" + "-".ljust(LEN_TYPE, "-") + "-|"
    SEP_OP += "-" + "-".ljust(LEN_TIER, "-") + "-|"
    SEP_OP += "-" + "-".ljust(LEN_CAT, "-") + "-|"
    SEP_OP += "-" + "-".ljust(LEN_DESC, "-") + "-|"
    SEP_OP += "-" + "-".ljust(LEN_AMOUNT, "-") + "-|"

    # # Operation header
    # HEADER_OP = "|"
    # HEADER_OP += " " + "date".ljust(LEN_DATE, " ") + " |"
    # HEADER_OP += " " + "type".ljust(LEN_TYPE, ' ') + " |"
    # HEADER_OP += " " + "tier".ljust(LEN_TIER, ' ') + " |"
    # HEADER_OP += " " + "category".ljust(LEN_CAT, ' ') + " |"
    # HEADER_OP += " " + "description".ljust(LEN_DESC, ' ') + " |"
    # HEADER_OP += " " + "amount".ljust(LEN_AMOUNT, ' ') + " |"

    # Operation missing
    MISS_OP = "|"
    MISS_OP += " " + "...".ljust(LEN_DATE, ' ') + " |"
    MISS_OP += " " + "...".ljust(LEN_TYPE, ' ') + " |"
    MISS_OP += " " + "...".ljust(LEN_TIER, ' ') + " |"
    MISS_OP += " " + "...".ljust(LEN_CAT, ' ') + " |"
    MISS_OP += " " + "...".ljust(LEN_DESC, ' ') + " |"
    MISS_OP += " " + "...".ljust(LEN_AMOUNT, ' ') + " |"

    def __init__(self, account : Account) -> None :

        # Account
        self.account : Account = account

        # Windows list
        self.pWin : List[Window] = [None] * (self.WIN_ID_LAST + 1)

    def main(self, winMain: Window) -> None :

        # Main window height
        self.WIN_MAIN_H = curses.LINES
        WIN_MAIN_W = curses.COLS - 2

        WIN_CMD_H = 3
        WIN_CMD_W = int(2 * WIN_MAIN_W / 3) - 2
        WIN_CMD_Y = self.WIN_MAIN_H - WIN_CMD_H - 1
        WIN_CMD_X = 2

        WIN_INFO_H = int((self.WIN_MAIN_H - WIN_CMD_H) / 2) - 2
        WIN_INFO_W = int(WIN_MAIN_W / 3) - 2
        WIN_INFO_Y = 2
        WIN_INFO_X = WIN_MAIN_W - WIN_INFO_W - 1

        WIN_INPUT_H = WIN_INFO_H
        WIN_INPUT_W = WIN_INFO_W
        WIN_INPUT_Y = WIN_INFO_Y + WIN_INFO_H + 1
        WIN_INPUT_X = WIN_INFO_X

        WIN_STATUS_H = WIN_CMD_H
        WIN_STATUS_W = WIN_INFO_W
        WIN_STATUS_Y = WIN_CMD_Y
        WIN_STATUS_X = WIN_INFO_X

        curses.init_pair(self.COLOR_PAIR_ID_RED_BLACK, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(self.COLOR_PAIR_ID_GREEN_BLACK, curses.COLOR_GREEN, curses.COLOR_BLACK)

        self.pWin[self.WIN_ID_MAIN] = winMain

        winInfo = curses.newwin(WIN_INFO_H, WIN_INFO_W, WIN_INFO_Y, WIN_INFO_X)
        self.pWin[self.WIN_ID_INFO] = winInfo

        winInput = curses.newwin(WIN_INPUT_H, WIN_INPUT_W, WIN_INPUT_Y, WIN_INPUT_X)
        winInput.keypad(True)
        self.pWin[self.WIN_ID_INPUT] = winInput

        winCmd = curses.newwin(WIN_CMD_H, WIN_CMD_W, WIN_CMD_Y, WIN_CMD_X)
        self.pWin[self.WIN_ID_CMD] = winCmd

        winStatus = curses.newwin(WIN_STATUS_H, WIN_STATUS_W, WIN_STATUS_Y, WIN_STATUS_X)
        self.pWin[self.WIN_ID_STATUS] = winStatus

        self.ACCOUNT_browse()

    def ACCOUNT_disp(self, iStatFirst : int, statHl : Statement) -> None :

        # Number of statements to display
        nStatDisp : int = self.WIN_MAIN_H - 11
        if len(self.account.pStat) < nStatDisp:
            nStatDisp = len(self.account.pStat)
        # TODO
        # iStatLast

        # Use main window
        win : Window = self.pWin[self.WIN_ID_MAIN]

        win.clear()
        win.border()
        win.move(0, 2)
        win.addstr(" STATEMENTS ", A_BOLD)

        (y, x) = (2, 2)
        win.addstr(y, x, f"{self.SEP_STAT}")
        y = y + 1

        win.addstr(y, x, f"| ")
        win.addstr("name".ljust(LEN_NAME), A_BOLD)
        win.addstr(" | ")
        win.addstr("date".ljust(LEN_DATE), A_BOLD)
        win.addstr(" | ")
        win.addstr("start".ljust(LEN_AMOUNT), A_BOLD)
        win.addstr(" | ")
        win.addstr("end".ljust(LEN_AMOUNT), A_BOLD)
        win.addstr(" | ")
        win.addstr("diff".ljust(LEN_AMOUNT), A_BOLD)
        win.addstr(" | ")
        win.addstr("err".ljust(LEN_AMOUNT), A_BOLD)
        win.addstr(" |")
        y = y + 1

        # Statement separator or missing
        if iStatFirst == 0:
            win.addstr(y, x, self.SEP_STAT)
        else:
            win.addstr(y, x, self.MISS_STAT)
        y = y + 1

        # For each statement in display range
        # TODO
        # for iStat in range(iStatFirst, iStatLast):
        iStat = iStatFirst
        while iStat < len(self.account.pStat) and iStat < iStatFirst + nStatDisp:

            stat : Statement = self.account.pStat[iStat]

            dispFlag = A_NORMAL
            if stat == statHl:
                dispFlag += A_STANDOUT

            win.addstr(y, x, "| ")
            win.addstr(stat.name.ljust(LEN_NAME), dispFlag)
            win.addstr(" | ")
            win.addstr(stat.date.strftime(FMT_DATE).ljust(LEN_DATE), dispFlag)
            win.addstr(" | ")
            win.addstr(str(stat.balStart).ljust(LEN_AMOUNT), dispFlag)
            win.addstr(" | ")
            win.addstr(str(stat.balEnd).ljust(LEN_AMOUNT), dispFlag)
            win.addstr(" | ")
            balanceDiff = round(stat.balEnd - stat.balStart, 2)
            if balanceDiff >= 0.0:
                win.addstr(str(balanceDiff).ljust(LEN_AMOUNT),
                    curses.color_pair(self.COLOR_PAIR_ID_GREEN_BLACK))
            else:
                win.addstr(str(balanceDiff).ljust(LEN_AMOUNT),
                    curses.color_pair(self.COLOR_PAIR_ID_RED_BLACK))
            win.addstr(" | ")
            balanceErr = round(stat.balStart + stat.opSum - stat.balEnd, 2)
            if balanceErr == 0.0:
                win.addstr(str(balanceErr).ljust(LEN_AMOUNT),
                    curses.color_pair(self.COLOR_PAIR_ID_GREEN_BLACK))
            else:
                win.addstr(str(balanceErr).ljust(LEN_AMOUNT),
                    curses.color_pair(self.COLOR_PAIR_ID_RED_BLACK))
            win.addstr(" |")
            y = y + 1

            iStat = iStat + 1

        # Statement separator or missing
        if iStat == len(self.account.pStat):
            win.addstr(y, x, self.SEP_STAT)
        else:
            win.addstr(y, x, self.MISS_STAT)
        y = y + 1

        # Slider
        # Move to top right of table
        (y, x) = (5, win.getyx()[1])
        for i in range(int(iStatFirst * nStatDisp / len(self.account.pStat))):
            win.addstr(y, x, " ")
            y = y + 1
        for i in range(int(nStatDisp * nStatDisp / len(self.account.pStat)) + 1):
            win.addstr(y, x, " ", A_STANDOUT)
            y = y + 1

        win.refresh()

    def ACCOUNT_browse(self) -> None :

        # Index of first displayed statement
        iStatFirst : int = 0
        # Highlighted statement
        statHl : Statement = self.account.pStat[0]

        while True:

            self.ACCOUNT_disp(iStatFirst, statHl)

            # Status window
            win : Window = self.pWin[self.WIN_ID_STATUS]
            win.clear()
            win.border()
            win.addstr(0, 2, " STATUS ", A_BOLD)
            if self.account.bUnsav == True:
                win.addstr(1, 2, "Unsaved", curses.color_pair(self.COLOR_PAIR_ID_RED_BLACK))
            else:
                win.addstr(1, 2, "Saved", curses.color_pair(self.COLOR_PAIR_ID_GREEN_BLACK))
            win.refresh()

            # Command window
            win : Window = self.pWin[self.WIN_ID_CMD]
            win.clear()
            win.border()
            win.addstr(0, 2, " COMMANDS ", A_BOLD)
            sCmd = "Add : INS/+, Del : DEL/-"
            sCmd = sCmd + ", Open : ENTER"
            sCmd = sCmd + ", Save : S, Ret : ESCAPE"
            win.addstr(1, 2, sCmd)
            win.refresh()

            key = self.pWin[self.WIN_ID_MAIN].getkey()

            # Highlight previous statement
            if key == "KEY_UP":

                # Highlight previous statement
                iStatHl = self.account.pStat.index(statHl) - 1
                if iStatHl < 0:
                    iStatHl = 0
                statHl = self.account.pStat[iStatHl]

                # If out of display range
                if iStatHl < iStatFirst:
                    # Previous page
                    iStatFirst = iStatFirst - 1
                    if iStatFirst < 0:
                        iStatFirst = 0

            # Highlight next statement
            if key == "KEY_DOWN":

                # Highlight next statement
                iStatHl = self.account.pStat.index(statHl) + 1
                if iStatHl >= len(self.account.pStat):
                    iStatHl = len(self.account.pStat) - 1
                statHl = self.account.pStat[iStatHl]

                # If out of display range
                if iStatHl - iStatFirst >= self.WIN_MAIN_H - 11:
                    # Next page
                    iStatFirst = iStatFirst + 1
                    if iStatFirst > len(self.account.pStat) - (self.WIN_MAIN_H - 11):
                        iStatFirst = len(self.account.pStat) - (self.WIN_MAIN_H - 11)

            # Previous page
            elif key == "KEY_PPAGE":

                # Previous page
                iStatFirst = iStatFirst - 3
                if iStatFirst < 0:
                    iStatFirst = 0

                # If out of display range
                iStatHl = self.account.pStat.index(statHl)
                if iStatHl < iStatFirst:
                    statHl = self.account.pStat[iStatFirst]
                elif iStatHl >= iStatFirst + self.WIN_MAIN_H - 11:
                    statHl = self.account.pStat[iStatFirst + self.WIN_MAIN_H - 11 - 1]

            # Next page
            elif key == "KEY_NPAGE":

                # Next page
                iStatFirst = iStatFirst + 3
                if iStatFirst > len(self.account.pStat) - (self.WIN_MAIN_H - 11):
                    iStatFirst = len(self.account.pStat) - (self.WIN_MAIN_H - 11)
                    if iStatFirst < 0:
                        iStatFirst = 0

                # If out of display range
                iStatHl = self.account.pStat.index(statHl)
                if iStatHl < iStatFirst:
                    statHl = self.account.pStat[iStatFirst]
                elif iStatHl >= iStatFirst + self.WIN_MAIN_H - 11:
                    statHl = self.account.pStat[iStatFirst + self.WIN_MAIN_H - 11 - 1]

            # Add statement
            elif key == "KEY_IC" or key == "+":
                self.ACCOUNT_addStat()

            # Delete highlighted statement
            elif key == "KEY_DC" or key == "-":
                self.ACCOUNT_delStat(statHl)
                # Reset highlighted statement
                statHl = self.account.pStat[0]

            # Open highligthed statement
            elif key == "\n":
                self.STAT_browse(statHl)

            elif key == "s":
                self.account.save()
                pass

            elif key == '\x1b':
                if self.account.bUnsav == True:
                    # Input window
                    win : Window = self.pWin[self.WIN_ID_INPUT]
                    win.clear()
                    win.border()
                    win.addstr(0, 2, " UNSAVED CHANGES ", A_BOLD)
                    win.addstr(2, 2, "Save ? (y/n) : ")
                    cSave = win.getch()
                    if cSave != ord('n'):
                        win.addstr(4, 2, f"Saving")
                        win.refresh()
                        time.sleep(1)
                        self.account.save()
                    else:
                        win.addstr(4, 2, f"Discard changes", curses.color_pair(self.COLOR_PAIR_ID_RED_BLACK))
                        win.refresh()
                        time.sleep(1)
                break

    def ACCOUNT_addStat(self) -> None :

        # Use input window
        win : Window = self.pWin[self.WIN_ID_INPUT]

        win.clear()
        win.border()
        win.move(0, 2)
        win.addstr(" STATEMENT ", A_BOLD)

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
            win.addstr(y, x, "date :                  ")
            win.addstr(y, x, "date : ")
            sVal = win.getstr().decode(encoding="utf-8")
            try:
                date = datetime.strptime(sVal, FMT_DATE)
                bConvert = True
            except:
                pass

        y = y + 1

        bConvert = False
        while bConvert != True:
            win.addstr(y, x, "start balance :         ")
            win.addstr(y, x, "start balance : ")
            sVal = win.getstr().decode(encoding="utf-8")
            try:
                balStart = float(sVal)
                bConvert = True
            except:
                pass

        y = y + 1

        bConvert = False
        while bConvert != True:
            win.addstr(y, x, "end balance :           ")
            win.addstr(y, x, "end balance : ")
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
        self.account.insertStat(stat)

    def ACCOUNT_delStat(self, stat : Statement) -> None :

        # Input window
        win : Window = self.pWin[self.WIN_ID_INPUT]
        win.clear()
        win.border()
        win.addstr(0, 2, " DELETE STATEMENT ", A_BOLD)
        win.addstr(2, 2, "Confirm ? (y/n) : ")
        cConfirm = win.getch()
        if cConfirm != ord('y'):
            win.addstr(7, 2, f"Canceled", curses.color_pair(self.COLOR_PAIR_ID_RED_BLACK))
            win.refresh()
            time.sleep(1)
            return

        # Delete highlighted statement
        self.account.delStat(stat)

    def STAT_dispOps(self, stat : Statement,
        iOpFirst : int, opHl : Operation, pOpSel : List[Operation]) -> None :

        nOpDisp = self.WIN_MAIN_H - 11
        if len(stat.pOp) < nOpDisp:
            nOpDisp = len(stat.pOp)

        # Use main window
        win : Window = self.pWin[self.WIN_ID_MAIN]

        win.clear()
        win.border()
        win.move(0, 2)
        win.addstr(" STATEMENT ", A_BOLD)

        (y, x) = (2, 2)
        win.addstr(y, x, self.SEP_OP)
        y = y + 1

        win.addstr(y, x, "| ")
        win.addnstr("date".ljust(LEN_DATE), LEN_DATE, A_BOLD)
        win.addstr(" | ")
        win.addnstr("type".ljust(LEN_TYPE), LEN_TYPE, A_BOLD)
        win.addstr(" | ")
        win.addnstr("tier".ljust(LEN_TIER), LEN_TIER, A_BOLD)
        win.addstr(" | ")
        win.addnstr("cat".ljust(LEN_CAT), LEN_CAT, A_BOLD)
        win.addstr(" | ")
        win.addnstr("desc".ljust(LEN_DESC), LEN_DESC, A_BOLD)
        win.addstr(" | ")
        win.addnstr("amount".ljust(LEN_AMOUNT), LEN_AMOUNT, A_BOLD)
        win.addstr(" |")
        y = y + 1

        # Operation separator or missing
        if iOpFirst == 0:
            win.addstr(y, x, self.SEP_OP)
        else:
            win.addstr(y, x, self.MISS_OP)
        y = y + 1

        opIdx = iOpFirst
        while opIdx < len(stat.pOp) and opIdx < iOpFirst + nOpDisp:

            op = stat.pOp[opIdx]

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

        # Operation separator or missing
        if opIdx == len(stat.pOp):
            win.addstr(y, x, self.SEP_OP)
        else:
            win.addstr(y, x, self.MISS_OP)
        y = y + 1

        if len(stat.pOp) != 0:
            # Slider
            # Move to top right of table
            (y, x) = (5, win.getyx()[1])
            for i in range(int(iOpFirst * nOpDisp / len(stat.pOp))):
                win.addstr(y, x, " ")
                y = y + 1
            for i in range(int(nOpDisp * nOpDisp / len(stat.pOp))):
                win.addstr(y, x, " ", A_STANDOUT)
                y = y + 1

        win.refresh()

    def STAT_dispFields(self, stat : Statement) -> None :

        # Use info window
        win : Window = self.pWin[self.WIN_ID_INFO]

        win.clear()
        win.border()
        win.move(0, 2)
        win.addstr(" INFO ", A_BOLD)

        (y, x) = (2, 2)
        win.addstr(y, x, f"name : {stat.name}")
        y = y + 1
        win.addstr(y, x, f"date : {stat.date.strftime(FMT_DATE)}")
        y = y + 1
        win.addstr(y, x, f"start : {stat.balStart}")
        y = y + 1
        win.addstr(y, x, f"end : {stat.balEnd}")
        y = y + 1
        win.addstr(y, x, f"actual end : {(stat.balStart + stat.opSum):.2f}")
        y = y + 1
        balanceDiff = round(stat.balEnd - stat.balStart, 2)
        win.addstr(y, x, f"diff : ")
        if balanceDiff >= 0.0:
            win.addstr(str(balanceDiff), curses.color_pair(self.COLOR_PAIR_ID_GREEN_BLACK))
        else:
            win.addstr(str(balanceDiff), curses.color_pair(self.COLOR_PAIR_ID_RED_BLACK))
        y = y + 1
        balanceErr = round(stat.balStart + stat.opSum - stat.balEnd, 2)
        win.addstr(y, x, f"err : ")
        if balanceErr == 0.0:
            win.addstr(str(balanceErr), curses.color_pair(self.COLOR_PAIR_ID_GREEN_BLACK))
        else:
            win.addstr(str(balanceErr), curses.color_pair(self.COLOR_PAIR_ID_RED_BLACK))
        y = y + 1

        win.refresh()

    def STAT_browse(self, stat : Statement) -> None :

        # Selected operations list
        pOpSel : List[Operation] = []

        # First displayed operation
        iOpFirst : int = 0

        # Highlighted operation
        if len(stat.pOp) != 0:
            opHl : Operation = stat.pOp[0]
        else:
            opHl : Operation = None

        while True:

            self.STAT_dispOps(stat, iOpFirst, opHl, pOpSel)
            self.STAT_dispFields(stat)

            # Command window
            win : Window = self.pWin[self.WIN_ID_CMD]
            win.clear()
            win.border()
            win.addstr(0, 2, " COMMANDS ", A_BOLD)
            sCmd = "Add : INS/+, Del : DEL/-"
            sCmd = sCmd + ", Dupl : D, (Un)sel : SPACE, Move : M "
            sCmd = sCmd + ", Open : ENTER"
            sCmd = sCmd + ", Save : S, Ret : ESCAPE"
            win.addstr(1, 2, sCmd)
            win.refresh()

            # Status window
            win : Window = self.pWin[self.WIN_ID_STATUS]
            win.clear()
            win.border()
            win.addstr(0, 2, " STATUS ", A_BOLD)
            if stat.bUnsav == True:
                win.addstr(1, 2, "Unsaved", curses.color_pair(self.COLOR_PAIR_ID_RED_BLACK))
            else:
                win.addstr(1, 2, "Saved", curses.color_pair(self.COLOR_PAIR_ID_GREEN_BLACK))
            win.refresh()

            key = self.pWin[self.WIN_ID_MAIN].getkey()

            # Highlight previous operation
            if key == "KEY_UP":

                opHlIdx = stat.pOp.index(opHl) - 1
                if opHlIdx < 0:
                    opHlIdx = 0
                opHl = stat.pOp[opHlIdx]

                # If out of display range
                if opHlIdx < iOpFirst:
                    # Previous page
                    iOpFirst = iOpFirst - 1
                    if iOpFirst < 0:
                        iOpFirst = 0

            # Highlight next operation
            elif key == "KEY_DOWN":

                opHlIdx = stat.pOp.index(opHl) + 1
                if opHlIdx >= len(stat.pOp):
                    opHlIdx = len(stat.pOp) - 1
                opHl = stat.pOp[opHlIdx]

                # If out of display range
                if opHlIdx - iOpFirst >= self.WIN_MAIN_H - 11:
                    # Next page
                    iOpFirst = iOpFirst + 1
                    if iOpFirst > len(stat.pOp) - (self.WIN_MAIN_H - 11):
                        iOpFirst = len(stat.pOp) - (self.WIN_MAIN_H - 11)

            # Previous page
            elif key == "KEY_PPAGE":

                # Previous page
                iOpFirst = iOpFirst - 3
                if iOpFirst < 0:
                    iOpFirst = 0

                # If out of display range
                opHlIdx = stat.pOp.index(opHl)
                if opHlIdx < iOpFirst:
                    opHl = stat.pOp[iOpFirst]
                elif opHlIdx >= iOpFirst + self.WIN_MAIN_H - 11:
                    opHl = stat.pOp[iOpFirst + self.WIN_MAIN_H - 11 - 1]

            # Next page
            elif key == "KEY_NPAGE":

                # Next page
                iOpFirst = iOpFirst + 3
                if iOpFirst > len(stat.pOp) - (self.WIN_MAIN_H - 11):
                    iOpFirst = len(stat.pOp) - (self.WIN_MAIN_H - 11)
                    if iOpFirst < 0:
                        iOpFirst = 0

                # If out of display range
                opHlIdx = stat.pOp.index(opHl)
                if opHlIdx < iOpFirst:
                    opHl = stat.pOp[iOpFirst]
                elif opHlIdx >= iOpFirst + self.WIN_MAIN_H - 11:
                    opHl = stat.pOp[iOpFirst + self.WIN_MAIN_H - 11 - 1]

            # (Un)select operation
            elif key == " ":
                # If operation not selected
                if opHl not in pOpSel:
                    # Add operation to selected ones
                    pOpSel.append(opHl)
                # Else, operation selected
                else:
                    # Remove operation from selected ones
                    pOpSel.remove(opHl)

            # Add operation
            elif key == "KEY_IC" or key == "+":
                self.STAT_addOp(stat)

            # Delete operation(s)
            elif key == "KEY_DC" or key == "-":

                # If no selected operations
                if len(pOpSel) == 0:
                    # Selected is highlighted operation
                    pOpSel.append(opHl)

                # Highlight closest operation
                opHl = stat.getClosestOp(pOpSel)

                # Delete selected operations from statement
                self.STAT_delOps(stat, pOpSel)

                # Clear select operations
                pOpSel.clear()

            # Move selected operations
            elif key == "m":

                # If no selected operations
                if len(pOpSel) == 0:
                    # Selected is highlighted operation
                    pOpSel.append(opHl)

                # Highlight closest operation
                opHl = stat.getClosestOp(pOpSel)

                # Move selected operations from statement
                self.STAT_moveOps(stat, pOpSel)

                # Clear select operations
                pOpSel.clear()

            # Open highlighted operation
            elif key == "\n":

                (bEdit, bDateEdit) = self.OP_browse(opHl)
                # If operation edited
                if bEdit == True:
                    stat.bUnsav = True
                    # If date edited
                    if bDateEdit == True:
                        # Delete and insert opearion from/to statement
                        # To update index
                        stat.delOps([opHl])
                        stat.insertOp(opHl)

            # Duplicate highlighted operation
            elif key == "d":

                # Create new operation from highlighted one
                opNew = Operation(opHl.date, opHl.type, opHl.tier, opHl.cat, opHl.desc, opHl.amount)
                # Add new operation to statement
                stat.insertOp(opNew)
                # Highlight new operation
                opHl = opNew

            # Save
            elif key == "s":
                stat.save()

            # Exit
            elif key == '\x1b':
                if stat.bUnsav == True:
                    # Input window
                    win : Window = self.pWin[self.WIN_ID_INPUT]
                    win.clear()
                    win.border()
                    win.addstr(0, 2, " UNSAVED CHANGES ", A_BOLD)
                    win.addstr(2, 2, "Save ? (y/n) : ")
                    cSave = win.getch()
                    if cSave != ord('n'):
                        win.addstr(4, 2, f"Saving")
                        win.refresh()
                        time.sleep(1)
                        stat.save()
                    else:
                        win.addstr(4, 2, f"Discard changes", curses.color_pair(self.COLOR_PAIR_ID_RED_BLACK))
                        win.refresh()
                        time.sleep(1)
                        stat.reset()
                break

    def STAT_addOp(self, stat : Statement) -> None :

        # Create empty opeartion
        op = Operation(datetime.now(), "", "", "", "", 0.0)

        # Use input window
        win = self.pWin[self.WIN_ID_INPUT]

        # For each operation field
        for iField in range(op.IDX_AMOUNT + 1):

            self.OP_disp(op, iField)
            (y, x) = (win.getyx()[0], 2)

            win.addstr(y, x, "Value : ")
            win.keypad(False)
            curses.echo()
            sVal = win.getstr().decode(encoding="utf-8")
            win.keypad(True)
            curses.noecho()

            if sVal != "":
                op.setField(iField, sVal)

        stat.insertOp(op)

    def STAT_delOps(self, stat : Statement, pOp : List[Operation]) -> None:

        # Use input window
        win = self.pWin[self.WIN_ID_INPUT]

        win.clear()
        win.border()
        win.addstr(0, 2, " DELETE OPERATIONS ", A_BOLD)
        win.addstr(2, 2, f"Delete {len(pOp)} operations")
        win.addstr(4, 2, "Confirm ? (y/n) : ")
        cConfirm = win.getch()
        if cConfirm != ord('y'):
            win.addstr(7, 2, f"Canceled", curses.color_pair(self.COLOR_PAIR_ID_RED_BLACK))
            win.refresh()
            time.sleep(1)
            return

        stat.delOps(pOp)

    def STAT_moveOps(self, statSrc : Statement, pOp : List[Operation]) -> None :

        # Use input window
        win = self.pWin[self.WIN_ID_INPUT]

        win.clear()
        win.border()
        win.addstr(0, 2, " MOVE OPERATIONS ", A_BOLD)
        win.addstr(2, 2, f"Destination statement : ")
        win.addstr(3, 2, f"  Name (date) : ")
        curses.echo()
        sStatDstName = win.getstr().decode(encoding="utf-8")
        curses.noecho()
        statDst = account.getStatByName(sStatDstName)
        if statDst is None:
            win.addstr(5, 2, f"Destination statement", curses.color_pair(self.COLOR_PAIR_ID_RED_BLACK))
            win.addstr(6, 2, f"not found", curses.color_pair(self.COLOR_PAIR_ID_RED_BLACK))
            win.refresh()
            time.sleep(1)
            return

        win.clear()
        win.border()
        win.addstr(0, 2, " MOVE OPERATIONS ", A_BOLD)
        win.addstr(2, 2, f"Move {len(pOp)} operations")
        win.addstr(3, 2, f"To statement {statDst.name}")
        win.addstr(5, 2, "Confirm ? (y/n) : ")
        cConfirm = win.getch()
        if cConfirm != ord('y'):
            win.addstr(7, 2, f"Canceled", curses.color_pair(self.COLOR_PAIR_ID_RED_BLACK))
            win.refresh()
            time.sleep(1)
            return

        # For each operation
        for op in pOp:
            # Insert operation in target statement
            statDst.insertOp(op)
            # Delete operation from source statement
            statSrc.delOps([op])

        # Save source and destination statement
        statSrc.save()
        statDst.save()

    def OP_disp(self, op : Operation, iFieldHl : int) -> None :

        # Use input window
        win = self.pWin[self.WIN_ID_INPUT]

        win.clear()
        win.border()
        win.move(0, 2)
        win.addstr(" OPERATION ", A_BOLD)

        (y, x) = (2, 2)
        for iField in range(op.IDX_AMOUNT + 1):

            dispFlag = A_NORMAL
            if iField == iFieldHl:
                dispFlag = A_STANDOUT

            (sName, sVal) = op.getField(iField)
            win.addstr(y, x, f"{sName} : {sVal}", dispFlag)
            y = y + 1

        y = y + 1
        win.addstr(y, x, "")

        win.refresh()

    def OP_browse(self, op : Operation) -> Tuple[bool, bool]:

        bEdit = False
        bDateEdit = False
        iFieldHl = 0

        while True:

            self.OP_disp(op, iFieldHl)
            (y, x) = (self.pWin[self.WIN_ID_MAIN].getyx()[0], 2)
            y = y + 2

            key = self.pWin[self.WIN_ID_MAIN].getkey()

            # Highlight previous field
            if key == "KEY_UP":
                iFieldHl = iFieldHl - 1
                if iFieldHl < op.IDX_DATE:
                    iFieldHl = op.IDX_AMOUNT

            # Highlight next field
            elif key == "KEY_DOWN":
                iFieldHl = iFieldHl + 1
                if iFieldHl > op.IDX_AMOUNT:
                    iFieldHl = op.IDX_DATE

            # Edit highlighted field
            elif key == "\n":

                # Use input window
                win : Window = self.pWin[self.WIN_ID_INPUT]
                win.addstr("Value : ")
                win.keypad(False)
                curses.echo()
                sVal = win.getstr().decode(encoding="utf-8")
                win.keypad(True)
                curses.noecho()

                if sVal != "":

                    status = op.setField(iFieldHl, sVal)
                    if status == ERROR:
                        continue

                    # Field edited
                    bEdit = True
                    # If date edited
                    if iFieldHl == op.IDX_DATE:
                        bDateEdit = True

            # Exit
            elif key == '\x1b':
                break

        return (bEdit, bDateEdit)

if __name__ == "__main__":

    account = Account()

    # Curses
    display = DisplayCurses(account)
    wrapper(display.main)

    sys.exit(0)
