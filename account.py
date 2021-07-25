
import csv
import curses
from curses import *
from datetime import datetime
from typing import List

from utils import *
from statement import Statement

class Account(object):

    def __init__(self) -> None:

        self.filePath = "statements.csv"

        # Statements list
        self.pStat : List[Statement] = list()

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

        # TODO
        self.bUnsav = False

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

    def getStatByName(self, sName: str) -> Statement:

        for stat in self.pStat:
            if stat.name == sName:
                return stat
        return None

    def dispStats(self, win, iStatFirst: int, statHl: Statement) -> None:

        pass

    def editStats(self, pWin) -> None:

        pass

    # Insert statement
    def insertStat(self, stat: Statement) -> int:

        # Find index
        idx = 0
        while idx < len(self.pStat) and stat.date > self.pStat[idx].date:
            idx = idx + 1

        # Insert statement at dedicated index
        self.pStat.insert(idx, stat)

        return OK

    def addStat(self, win) -> None:

        pass
