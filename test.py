
import curses
from curses import *
import sys

def main(win_main):

    win = curses.newwin(10, 10)
    win.keypad(True)

    while True:

        ch = win.getch()
        try:
            print(int(ch))
        except ValueError:
            print("no int")
        print(ch)

if __name__ == "__main__":

    wrapper(main)

    sys.exit(0)
