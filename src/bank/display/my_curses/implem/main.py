



import curses
from curses import *
from datetime import datetime
from enum import IntEnum
import logging
from typing import (TYPE_CHECKING, Any, List, Union, Tuple)

from bank.display.my_curses.main import (NoOverrideError, ColorPairId, WinId, DisplayerMain)
from bank.display.my_curses.item_display import DisplayerItem
from bank.display.my_curses.container_display import DisplayerContainer

from bank.account import Account
from bank.statement import Statement
from bank.operation import Operation

from bank.utils.clipboard import Clipboard
from bank.utils.my_date import FMT_DATE
from bank.utils.return_code import RetCode

if TYPE_CHECKING:
    from _curses import _CursesWindow
    Window = _CursesWindow
else:
    from typing import Any
    Window = Any

class FieldLen():
    # Length for display padding

    LEN_DATE = 10
    LEN_NAME = LEN_DATE
    LEN_MODE = 8
    LEN_TIER = 18
    LEN_CAT = 10
    LEN_DESC = 34
    LEN_AMOUNT = 8
