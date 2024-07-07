#!/usr/bin/env python3

from argparse import ArgumentParser
from datetime import date, datetime
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator
import numpy as np
import tkinter as tk
from typing import Any, List, Dict

from bank.internal import Wallet
from bank.utils import FMT_DATE

FMT_DATE_MONTH = "%Y-%m"

DATE_START = date(2019, 1, 1)
DATE_END = date(2024, 12, 1)

BAL_MIN = -5000
BAL_MAX = 50000
BAL_STEP_MAJ = 5000
BAL_STEP_MIN = 1000

def get_month_delta(_date: date):
    return (_date.year - DATE_START.year) * 12 + _date.month - DATE_START.month

def date_from_month_delta(month_delta: int):
    return date(DATE_START.year + int(month_delta / 12), month_delta % 12 + 1, 1)

def datetime_from_date(_date: date):
    return datetime(_date.year, _date.month, _date.day)

def datetime_from_month_delta(month_delta: int):
    return datetime_from_date(date_from_month_delta(month_delta))

def get_bal_str(bal: float):
    return f"{int(bal):_}"

def main():
    parser = ArgumentParser()
    parser.add_argument("data_dir", type=str, action="store",
        default="data", help="data folder")
    parser.add_argument("wallet_name", type=str, action="store",
        default="main", help="wallet name")
    parser.add_argument("-d", "--debug", action="store_true", help="enable debug log")
    args = parser.parse_args()

    wallet = Wallet(args.data_dir, args.wallet_name)

    # window = tk.Tk()
    # window.title("Hello World")

    # def handle_button_press(event):
    #     window.destroy()

    # button = tk.Button(text="My simple app.")
    # # button.bind("", handle_button_press)
    # button.pack()

    # # Start the event loop.
    # window.mainloop()

    fig, ax = plt.subplots(figsize=(10, 7))

    month_delta_list = [md for md in range(get_month_delta(DATE_START), get_month_delta(DATE_END))]

    for account in wallet.account_list:
        if "lbc" in account.name.lower():
            continue

        color = "grey"
        if "ce" in account.name.lower():
            color = "red"
        elif "nef" in account.name.lower():
            color = "green"
        elif "natixis" in account.name.lower():
            color = "blue"
        elif "carbon" in account.name.lower():
            color = "orange"

        month_delta_list: List[int] = []
        bal_list: List[float] = []
        for stat in account.stat_list:
            if stat.date.date() < DATE_START or stat.date.date() > DATE_END:
                continue
            month_delta = get_month_delta(stat.date)
            month_delta_list += [month_delta]
            bal_list += [account.get_bal_at(datetime_from_month_delta(month_delta))]

        ax.plot(month_delta_list, bal_list, marker="+", linestyle="-", color=color)

    # Plot balance sum
    month_delta_list: List[int] = []
    bal_sum_list: List[float] = []
    for month_delta in range(get_month_delta(DATE_START), get_month_delta(DATE_END)):
        month_delta_list += [month_delta]
        bal_sum = 0.0
        for account in wallet.account_list:
            if "lbc" in account.name.lower():
                continue
            bal_sum += account.get_bal_at(datetime_from_month_delta(month_delta))
        bal_sum_list += [bal_sum]
    ax.plot(month_delta_list, bal_sum_list, marker="+", linestyle="-", color="grey")

    ax.set_xlim(get_month_delta(DATE_START), get_month_delta(DATE_END))
    ax_x = ax.get_xaxis()
    x_tick_major_list = [get_month_delta(date(year, 1, 1)) for year in range(DATE_START.year, DATE_END.year + 1)]
    x_tick_minor_list: List[int] = []
    for year in range(DATE_START.year, DATE_END.year + 1):
        x_tick_minor_list += [get_month_delta(date(year, month, 1)) for month in range(1, 12 + 1)]
    ax_x.set_ticks(x_tick_major_list)
    ax_x.set_ticks(x_tick_minor_list, minor=True)
    ax_x.set_ticklabels(str(date_from_month_delta(month_delta).year) for month_delta in x_tick_major_list)
    ax_x.set_major_formatter(FuncFormatter(
        lambda x, p: date_from_month_delta(int(x)).strftime(FMT_DATE_MONTH)))

    ax.set_ylim(BAL_MIN, BAL_MAX)
    ax_y = ax.get_yaxis()
    ax_y.set_ticks([bal for bal in range(BAL_MIN, BAL_MAX, BAL_STEP_MAJ)])
    ax_y.set_ticks([bal for bal in range(BAL_MIN, BAL_MAX, BAL_STEP_MIN)], minor=True)
    ax_y.set_major_formatter(FuncFormatter(lambda x, p: get_bal_str(x)))

    plt.grid(True, "both", "both")
    plt.show()

if __name__ == "__main__":
    main()
