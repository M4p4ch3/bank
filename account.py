
import csv
import curses
from curses import *
from datetime import datetime
from typing import List

from utils import *
from statement import Statement

class Account(object):

    def __init__(self) -> None:

        status : int = OK

        self.filePath = "statements.csv"

        # Statements list
        self.pStat : List[Statement] = list()

        status = self.read()
        if status != OK:
            return status

        self.bUnsav : bool = False

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

    def getStatByName(self, sStatName: str) -> Statement:

        for stat in self.pStat:
            if stat.name == sStatName:
                return stat

        return None

    def read(self) -> int:

        try:
            # Open statements CSV file
            statsFile = open(self.filePath, "r")
        except:
            # TODO
            # log
            return ERROR

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

        return OK

    # Write to CSV file
    def write(self) -> int:

        try:
            # Open CSV file
            file = open(self.filePath, "w")
        except:
            return ERROR

        fileCsv = csv.writer(file, delimiter=',', quotechar='"')

        # For each statement
        for stat in self.pStat:

            # Create statement line
            statCsv = [stat.name, str(stat.balStart), str(stat.balEnd)]

            try:
                # Write statement line to CSV file
                fileCsv.writerow(statCsv)
            except:
                return ERROR

        self.bUnsav = False

        file.close()

        return OK

    def save(self) -> int:

        status : int = OK

        status = self.write()
        if status != OK:
            return ERROR

        self.bUnsav = False

        return OK

    def insertStat(self, stat: Statement) -> int:

        # Find index
        idx = 0
        while idx < len(self.pStat) and stat.date > self.pStat[idx].date:
            idx = idx + 1

        # Insert statement at dedicated index
        self.pStat.insert(idx, stat)

        self.bUnsav = True

        return OK

    def delStat(self, stat : Statement) -> int:

        try:
            self.pStat.remove(stat)
        except:
            return ERROR

        self.bUnsav = True

        return OK
