
"""
Statement
"""

import csv
from datetime import datetime
from typing import (List, Tuple)

from utils import (OK, ERROR, FMT_DATE)
from operation import Operation

class Statement():
    """
    Statement
    """

    # Field index
    IDX_INVALID = -1
    IDX_DATE = 0
    IDX_BAL_START = 1
    IDX_BAL_END = 2
    IDX_LAST = IDX_BAL_END

    def __init__(self, name: str, bal_start: float, bal_end: float) -> None:

        self.name: str = name
        self.file_path: str = f"statements/{name}.csv"
        try:
            self.date: datetime = datetime.strptime(name, FMT_DATE)
        except ValueError:
            self.date: datetime = datetime.now()
        self.bal_start: float = bal_start
        self.bal_end: float = bal_end
        self.op_sum: float = 0.0
        self.op_list: List[Operation] = list()
        self.is_unsaved: bool = False

    def get_str(self, indent: int = 0) -> str:
        """
        Get string representation
        """


        indent_str = ""
        for _ in range(indent):
            indent_str += "    "

        ret = ""
        ret += f"{indent_str}date : {self.date.strftime(FMT_DATE)}\n"
        ret += f"{indent_str}balance : [{str(self.bal_start)}, {str(self.bal_end)}]\n"
        ret += f"{indent_str}operations sum : {str(self.op_sum)}\n"
        ret += f"{indent_str}balance diff : {str(self.op_sum - self.bal_end)}\n"
        ret += f"{indent_str}operations : [\n"
        for op in self.op_list:
            ret += f"{indent_str}    {{\n"
            ret += op.get_str(indent + 2) + "\n"
            ret += f"{indent_str}    }}\n"
        ret += f"{indent_str}]"

    def get_field(self, field_idx: int) -> Tuple[str, str]:
        """
        Get field (name, value), identified by field index
        Useful for iterating over fields
        """

        ret = ("", "")
        if field_idx == self.IDX_DATE:
            ret = ("date", self.date.strftime(FMT_DATE))
        elif field_idx == self.IDX_BAL_START:
            ret = ("start balance", str(self.bal_start))
        elif field_idx == self.IDX_BAL_END:
            ret = ("start balance", str(self.bal_end))
        return ret

    def get_closest_op(self, op_list: List[Operation]) -> Operation:
        """
        Get closest operation from list
        None if not found
        """

        # Operation to return
        op_ret: Operation = op_list[0]

        # While operation in list
        while (op_ret in op_list) and (op_ret is not None):

            # Get operation index in statement
            op_ret_idx = self.op_list.index(op_ret)

            # If first operation in list is first operation in statement
            if self.op_list.index(op_list[0]) == 0:
                # Search forward
                op_ret_idx = op_ret_idx + 1
            # Else, first operation in list is not first one
            else:
                # Search backward
                op_ret_idx = op_ret_idx - 1

            # If operation out of statement
            if op_ret_idx < 0 or op_ret_idx >= len(self.op_list):
                op_ret = None
            else:
                op_ret = self.op_list[op_ret_idx]

        return op_ret

    def set_field(self, field_idx, val_str) -> int:
        """
        Set field value, identified by field index, from string
        Useful for iterating over fields
        """

        if field_idx == self.IDX_DATE:
            try:
                self.date = datetime.strptime(val_str, FMT_DATE)
            except ValueError:
                return ERROR
        elif field_idx == self.IDX_BAL_START:
            try:
                self.bal_start = float(val_str)
            except ValueError:
                return ERROR
        elif field_idx == self.IDX_BAL_END:
            try:
                self.bal_end = float(val_str)
            except ValueError:
                return ERROR

        self.is_unsaved = True

        return OK

    def read(self) -> int:
        """
        Read from file
        """

        try:
            # Open CSV file
            file = open(self.file_path, "r")
            file_csv = csv.reader(file)
        except FileNotFoundError:
            # File not found
            # Create new statement
            file = open(self.file_path, "w+")
            file.close()
            # Don't proceed with read
            return OK

        # Clear operations list
        self.op_list.clear()
        # Reset operations sum
        self.op_sum = 0.0

        # For each operation line in statement CSV file
        for op_line in file_csv:

            # Create operation
            op_date = datetime.strptime(op_line[Operation.IDX_DATE], FMT_DATE)
            op = Operation(op_date, op_line[Operation.IDX_MODE], op_line[Operation.IDX_TIER],
                           op_line[Operation.IDX_CAT], op_line[Operation.IDX_DESC],
                           float(op_line[Operation.IDX_AMOUNT]))

            # Add operation to list
            self.op_list.append(op)

            # Update operations sum
            self.op_sum = self.op_sum + op.amount

        self.is_unsaved = False

        file.close()

        return OK

    def write(self) -> int:
        """
        Write CSV file
        """

        try:
            # Open CSV file
            file = open(self.file_path, "w")
        except FileNotFoundError:
            return ERROR

        file_csv = csv.writer(file, delimiter=',', quotechar='"')

        # For each operation
        for op in self.op_list:

            # TODO check if op has (date, op, tier, car desc, amount)

            # Create operation line
            op_csv = [op.date.strftime(FMT_DATE), op.mode, op.tier,
                      op.cat, op.desc, str(op.amount)]

            try:
                # Write operation line to CSV file
                file_csv.writerow(op_csv)
            # TODO add error type
            except:
                return ERROR

        self.is_unsaved = False

        file.close()

        return OK

    def reset(self) -> int:
        """
        Reset : Read
        """

        status: int = OK

        status = self.read()
        if status != OK:
            return ERROR

        return OK

    def save(self) -> int:
        """
        Save : Write
        """

        status: int = OK

        status = self.write()
        if status != OK:
            return ERROR

        return OK

    def insert_op(self, op: Operation) -> int:
        """
        Insert operation
        """

        # Find index
        idx = 0
        while idx < len(self.op_list) and op.date > self.op_list[idx].date:
            idx = idx + 1

        # Insert operation at dedicated index
        self.op_list.insert(idx, op)

        # Update operation sum
        self.op_sum += op.amount

        self.is_unsaved = True

        return OK

    def del_op_list(self, op_list: List[Operation]) -> None:
        """
        Delete operation list
        """

        # For each operation
        for op in op_list:
            # Remove operation from statement
            self.op_list.remove(op)
            # Update operation sum
            self.op_sum -= op.amount

        self.is_unsaved = True

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
    #             val_str = pWin[WIN_IDX_INPUT].get_str().decode(encoding="utf-8")
    #             pWin[WIN_IDX_INPUT].keypad(True)
    #             curses.noecho()

    #             if val_str != "":
    #                 bEdit = self.setField(idxSel, val_str)
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
    #     win.addstr(2, 2, f"{self.get_field(fiedlIdx)}")
    #     win.addstr(4, 2, "New value : ")
    #     win.keypad(False)
    #     curses.echo()
    #     val_str = win.get_str().decode(encoding="utf-8")
    #     win.keypad(True)
    #     curses.noecho()

    #     if val_str != "":
    #         self.setField(fiedlIdx, val_str)
