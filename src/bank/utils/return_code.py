"""
Error code
"""

from enum import IntEnum

class RetCode(IntEnum):
    """
    Return code
    """

    OK = 0
    ERROR = 1
    CANCEL = 2
    EXIT_SAVE = 3
    EXIT_NO_SAVE = 4
