
import curses
from curses import *
import sys

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

def main(win):

    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    account = Account()
    account.editStats(win)

if __name__ == "__main__":

    wrapper(main)
    sys.exit(0)
