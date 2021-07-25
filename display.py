
import curses
from curses import *
import sys
from typing import List

from utils import *
from account import Account

# # Edit (value, name) pair
# # Return : Edited value
# def edit(name: str, val) -> str:

#     if type(val) == str:
#         sVal = val
#     elif type(val) == int or type(val) == float:
#         sVal = str(val)
#     elif type(val) == datetime:
#         sVal =  val.strftime(FMT_DATE)
#     else:
#         print(f"ERROR : unhandled type {type(val)}")
#         return ERROR

#     bConvert = False
#     while bConvert == False:

#         sValEdit = input(f"- {name} ({sVal}) : ")

#         if sValEdit == "":

#             valEdit = val
#             bConvert = True

#         else:

#             try:
#                 if type(val) == str:
#                     valEdit = sValEdit
#                     bConvert = True
#                 elif type(val) == int:
#                     valEdit = int(sValEdit)
#                     bConvert = True
#                 elif type(val) == float:
#                     valEdit = float(sValEdit)
#                     bConvert = True
#                 elif type(val) == datetime:
#                     valEdit = datetime.strptime(sValEdit, FMT_DATE)
#                     bConvert = True
#             except ValueError:
#                 print(f"ERROR : convert {sValEdit} FAILED")

#     return valEdit

def main(winMain: Window):

    WIN_MAIN_H = curses.LINES
    WIN_MAIN_W = curses.COLS - 2

    WIN_CMD_H = 3
    WIN_CMD_W = int(2 * WIN_MAIN_W / 3) - 2
    WIN_CMD_Y = WIN_MAIN_H - WIN_CMD_H - 1
    WIN_CMD_X = 2

    WIN_INFO_H = int((WIN_MAIN_H - WIN_CMD_H) / 2) - 2
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

    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)

    winMain.border()
    winMain.addstr(0, 2, " MAIN ")
    # winMain.refresh()

    winInfo = curses.newwin(WIN_INFO_H, WIN_INFO_W, WIN_INFO_Y, WIN_INFO_X)
    winInfo.border()
    winInfo.addstr(0, 2, " INFO ")
    # winInfo.refresh()

    winInput = curses.newwin(WIN_INPUT_H, WIN_INPUT_W, WIN_INPUT_Y, WIN_INPUT_X)
    winInput.keypad(True)
    winInput.border()
    winInput.addstr(0, 2, " INPUT ")
    # winInput.refresh()

    winCmd = curses.newwin(WIN_CMD_H, WIN_CMD_W, WIN_CMD_Y, WIN_CMD_X)
    winCmd.border()
    winCmd.addstr(0, 2, " COMMANDS ")
    # winCmd.refresh()

    winStatus = curses.newwin(WIN_STATUS_H, WIN_STATUS_W, WIN_STATUS_Y, WIN_STATUS_X)
    winStatus.border()
    winStatus.addstr(0, 2, " STATUS ")
    # winStatus.refresh()

    pWin:List[Window] = list()
    pWin.append(winMain)
    pWin.append(winInfo)
    pWin.append(winInput)
    pWin.append(winCmd)
    pWin.append(winStatus)

    account = Account()
    account.editStats(pWin)

if __name__ == "__main__":

    wrapper(main)
    sys.exit(0)
