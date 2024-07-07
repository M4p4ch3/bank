"""
display/shell/implem/statement
"""

from datetime import datetime
from typing import (Any, List, Tuple)

from bank.display.shell.main import DisplayerMain
from bank.display.shell.item_display import DisplayerItem
from bank.display.shell.container_display import DisplayerContainer
from bank.display.shell.implem.main import (FieldLen, formart_trunc_padd, format_amount)
from bank.display.shell.implem.operation_display import DisplayerOperation

from bank.internal.statement import Statement
from bank.internal.operation import Operation

from bank.utils.my_date import FMT_DATE
from bank.utils.return_code import RetCode

class DisplayerStatement(DisplayerItem, DisplayerContainer):
    """
    Curses statement display
    """

    # Item separator
    SEPARATOR = "|"
    SEPARATOR += "-" + "-".ljust(FieldLen.LEN_DATE, "-") + "-|"
    SEPARATOR += "-" + "-".ljust(FieldLen.LEN_NAME, "-") + "-|"
    SEPARATOR += "-" + "-".ljust(FieldLen.LEN_AMOUNT, "-") + "-|"
    SEPARATOR += "-" + "-".ljust(FieldLen.LEN_AMOUNT, "-") + "-|"
    SEPARATOR += "-" + "-".ljust(FieldLen.LEN_AMOUNT, "-") + "-|"
    SEPARATOR += "-" + "-".ljust(FieldLen.LEN_AMOUNT, "-") + "-|"

    # Item header
    HEADER = "|"
    HEADER += " " + "date".ljust(FieldLen.LEN_DATE, " ") + " |"
    HEADER += " " + "name".ljust(FieldLen.LEN_NAME, " ") + " |"
    HEADER += " " + "start".ljust(FieldLen.LEN_AMOUNT, " ") + " |"
    HEADER += " " + "end".ljust(FieldLen.LEN_AMOUNT, " ") + " |"
    HEADER += " " + "diff".ljust(FieldLen.LEN_AMOUNT, " ") + " |"
    HEADER += " " + "error".ljust(FieldLen.LEN_AMOUNT, " ") + " |"

    # Item missing
    MISSING = "|"
    MISSING += " " + "...".ljust(FieldLen.LEN_DATE, " ") + " |"
    MISSING += " " + "...".ljust(FieldLen.LEN_NAME, " ") + " |"
    MISSING += " " + "...".ljust(FieldLen.LEN_AMOUNT, " ") + " |"
    MISSING += " " + "...".ljust(FieldLen.LEN_AMOUNT, " ") + " |"
    MISSING += " " + "...".ljust(FieldLen.LEN_AMOUNT, " ") + " |"
    MISSING += " " + "...".ljust(FieldLen.LEN_AMOUNT, " ") + " |"

    def __init__(self, disp: DisplayerMain, stat: Statement = None) -> None:

        # Init self item display
        DisplayerItem.__init__(self, disp)

        # Init container item display
        ope_disp = DisplayerOperation(disp)

        # Init container display
        DisplayerContainer.__init__(self, disp, ope_disp)

        # self.item_disp: DisplayerOperation = DisplayerOperation(None, disp)

        # Statement
        self.stat: Statement = stat

        self.field_nb = Statement.FieldIdx.LAST + 1

        self.title = "STATEMENT"
        self.subtitle = "OPERATIONS LIST"

    def get_container_name(self) -> str:
        """
        Get statement name
        """

        return self.stat.name

    def set_item(self, item: Statement) -> None:
        """
        Set statement
        """

        self.stat = item

    def get_item_field(self, field_idx: int) -> Tuple[str, str]:
        """
        Get field (name, value), identified by field index
        """

        ret = ("", "")
        if field_idx == Statement.FieldIdx.DATE:
            ret = ("date", self.stat.date.strftime(FMT_DATE))
        elif field_idx == Statement.FieldIdx.NAME:
            ret = ("name", self.stat.name)
        elif field_idx == Statement.FieldIdx.BAL_START:
            ret = ("start balance", str(self.stat.bal_start))
        elif field_idx == Statement.FieldIdx.BAL_END:
            ret = ("end balance", str(self.stat.bal_end))

        return ret

    def set_item_field(self, field_idx: int, val_str: str) -> bool:
        """
        Set field value, identified by field index, from string
        """

        is_edited = True

        if field_idx == Statement.FieldIdx.DATE:
            try:
                self.stat.date = datetime.strptime(val_str, FMT_DATE)
            except ValueError:
                is_edited = False
        elif field_idx == Statement.FieldIdx.NAME:
            self.stat.set_name(val_str)
        elif field_idx == Statement.FieldIdx.BAL_START:
            try:
                self.stat.bal_start = float(val_str)
            except ValueError:
                is_edited = False
        elif field_idx == Statement.FieldIdx.BAL_END:
            try:
                self.stat.bal_end = float(val_str)
            except ValueError:
                is_edited = False

        if is_edited:
            self.stat.file_sync = False

        return is_edited

    def get_container_item_list(self) -> List[Operation]:
        """
        Get statement operation list
        """

        return self.stat.ope_list

    def add_container_item(self, item: Operation) -> None:
        """
        Add statement operation
        """

        self.stat.add_ope(item)

    def add_container_item_list(self, item_list: List[Operation]) -> None:
        """
        Add statement operation list
        """

        self.stat.add_ope_list(item_list)

    def remove_container_item_list(self, item_list: List[Operation],
            force: bool = False) -> RetCode:
        """
        Remove statement operation list
        """

        ret = super().remove_container_item_list(item_list, force)
        if ret == RetCode.CANCEL:
            return ret

        # Confirmed
        self.stat.remove_ope_list(item_list)
        return RetCode.OK

    def remove_container_item(self, item: Operation) -> None:
        """
        Remove statement operation

        Args:
            operation (Operation): operation
        """

        self.stat.remove_ope(item)

    def edit_container_item(self, item: Operation) -> None:
        """
        Edit operation

        Args:
            stat (Operation): Operation
        """

        # (Remove, edit, add) to update statment lsit and fields

        self.stat.remove_ope(item)

        ope_disp = DisplayerOperation(self.disp, item)
        ope_disp.edit_item()

        self.stat.add_ope(item)

    def browse_container_item(self, item: Operation) -> None:
        """
        Browse operation
        """

        self.edit_container_item(item)

    def create_container_item(self) -> Operation:
        """
        Create statement operation
        """

        # Init operation
        operation: Operation = Operation(datetime.now(), "", "", "", "", 0.0)

        # Init operation display
        ope_disp = DisplayerOperation(self.disp, operation)

        # Set operation fields
        ope_disp.edit_item(force_iterate=True)

        return operation

    def display_item_line(self, win: Any,
                          win_y: int, win_x: int, flag) -> None:
        """
        Display item line

        Args:
            win (Any): Window
            win_y (int): Y in window
            win_x (int): X in window
            flag ([type]): Display flag
        """

        stat_line = "| "
        stat_line += formart_trunc_padd(self.stat.date.strftime(FMT_DATE), FieldLen.LEN_DATE)
        stat_line += " | "
        stat_line += formart_trunc_padd(self.stat.name, FieldLen.LEN_NAME)
        stat_line += " | "
        stat_line += format_amount(self.stat.bal_start, FieldLen.LEN_AMOUNT)
        stat_line += " | "
        stat_line += format_amount(self.stat.bal_end, FieldLen.LEN_AMOUNT)
        stat_line += " | "

        print(stat_line)

        bal_diff = round(self.stat.bal_end - self.stat.bal_start, 2)
        if bal_diff >= 0.0:
            print(format_amount(bal_diff, FieldLen.LEN_AMOUNT))
        else:
            print(format_amount(bal_diff, FieldLen.LEN_AMOUNT))

        print(" | ")

        bal_err = round(self.stat.bal_start + self.stat.ope_sum - self.stat.bal_end, 2)
        if bal_err == 0.0:
            print(format_amount(bal_err, FieldLen.LEN_AMOUNT))
        else:
            print(format_amount(bal_err, FieldLen.LEN_AMOUNT))

        print(" |")

    def display_container_info(self) -> None:
        """
        Display statement info
        """

        print(" INFO ")

        print(f"date : {self.stat.date.strftime(FMT_DATE)}")

        print(f"name : {self.stat.name}")

        print(f"balance start : {self.stat.bal_start}")

        print(f"balance end : {self.stat.bal_end}")

        bal_diff = round(self.stat.bal_end - self.stat.bal_start, 2)
        print("balance diff : ")
        if bal_diff >= 0.0:
            print(str(bal_diff))
        else:
            print(str(bal_diff))

        print(f"actual end : {(self.stat.bal_start + self.stat.ope_sum):.2f}")

        bal_err = round(self.stat.bal_start + self.stat.ope_sum - self.stat.bal_end, 2)
        print("balance error : ")
        if bal_err == 0.0:
            print(str(bal_err))
        else:
            print(str(bal_err))

        print("status : ")
        if self.stat.file_sync:
            print("Saved")
        else:
            print("Unsaved")

        print(f"clipboard : {self.disp.item_list_clipboard.get_len()} operations")

        if self.disp.cont_disp_last is not None:
            print(f"last stat : {self.disp.cont_disp_last.get_container_name()}")
        else:
            print("last stat : None")


    def save(self) -> None:
        """
        Stave statement
        """

        self.stat.write_dir()

    def exit(self) -> RetCode:
        """
        Exit statement browse
        """

        # If saved
        if self.stat.file_sync:
            # Exit
            return RetCode.OK

        # Unsaved changes

        ret = super().exit()

        if ret == RetCode.EXIT_SAVE:
            self.stat.write_dir()
            return RetCode.OK

        if ret == RetCode.EXIT_NO_SAVE:
            self.stat.read_dir()
            return RetCode.OK

        return RetCode.CANCEL
