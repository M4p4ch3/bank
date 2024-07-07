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

def get_month_delta(_date: date):
    return (_date.year - DATE_START.year) * 12 + _date.month - DATE_START.month

def get_date_from_month_delta(month_delta: int):
    return date(DATE_START.year + int(month_delta / 12), month_delta % 12 + 1, 1)

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

    # date_list = []
    # for year in range(2019, 2024 + 1):
    #     for month in range(1, 12 + 1):
    #         date_list += [date(year, month, 1).strftime(FMT_DATE_MONTH)]
    # print(date_list)

    fig, ax = plt.subplots(figsize=(10, 7))

    # month_delta_bal_sum_dict: Dict[int, float] = {}

    for account in wallet.account_list:
        print(account.name)
        color = "grey"
        if "ce" in account.name.lower():
            color = "red"
        elif "nef" in account.name.lower():
            color = "green"
        elif "natixis" in account.name.lower():
            color = "blue"
        elif "carbon" in account.name.lower():
            color = "orange"
        print(color)

        date_list = [stat.date.strftime(FMT_DATE_MONTH) for stat in account.stat_list if stat.date.date() < DATE_END]
        print(date_list)
        month_delta_list = [get_month_delta(stat.date) for stat in account.stat_list if stat.date.date() < DATE_END]
        print(month_delta_list)
        bal_list = [stat.bal_end for stat in account.stat_list if stat.date.date() < DATE_END]
        print(bal_list)
        # plt.plot(month_delta_list, bal_list, marker="+", linestyle="-", color=color)
        ax.plot(month_delta_list, bal_list, marker="+", linestyle="-", color=color)

        # for stat in account.stat_list:
        #     month_delta = get_month_delta(stat.date)
        #     if month_delta not in month_delta_bal_sum_dict:
        #         month_delta_bal_sum_dict[month_delta] = stat.bal_end
        #     else:
        #         month_delta_bal_sum_dict[month_delta] += stat.bal_end
        # print(month_delta_bal_sum_dict)

        continue

        date_bal_dict: Dict[str, float] = {}
        for stat in account.stat_list:
            date_bal_dict[stat.date.strftime(FMT_DATE_MONTH)] = stat.bal_end
        print(date_bal_dict)

        bal_list = []
        for _date in date_list:
            if _date in date_bal_dict:
                bal_list += [date_bal_dict[_date]]
            else:
                bal_list += [np.nan]
        print(bal_list)

        # bal_list = np.array(bal_list).astype(np.double)
        # mask = np.isfinite(bal_list)
        # print(bal_list[mask])
        # plt.plot(date_list[mask], bal_list[mask], marker="+", linestyle="-", color=color)

        plt.plot(date_list, bal_list, marker="+", linestyle="-", color=color)

        print()

    # plt.plot(date_list, bal_list, "+-", color="red")
    # plt.plot(date_list, bal_list, "+-")
    # plt.grid(True)

    month_delta_list: List[int] = []
    bal_sum_list: List[float] = []
    for month_delta in range(get_month_delta(DATE_START), get_month_delta(DATE_END)):
        month_delta_list += [month_delta]
        _date = get_date_from_month_delta(month_delta)
        bal_sum = 0.0
        for account in wallet.account_list:
            bal_sum += account.get_bal_at(datetime(_date.year, _date.month, _date.day))
        bal_sum_list += [bal_sum]

    ax.plot(month_delta_list, bal_sum_list, marker="+", linestyle="-", color="grey")

    ax.get_xaxis().set_major_formatter(FuncFormatter(
        lambda x, p: get_date_from_month_delta(int(x)).strftime(FMT_DATE_MONTH)))
    ax.get_yaxis().set_major_formatter(FuncFormatter(lambda x, p: get_bal_str(x)))

    ax.get_xaxis().set_ticks([get_month_delta(date(year, 1, 1)) for year in range(DATE_START.year, DATE_END.year + 1)])

    tick_x_minor_list: List[int] = []
    for year in range(DATE_START.year, DATE_END.year + 1):
        tick_x_minor_list += [get_month_delta(date(year, month, 1)) for month in range(1, 12 + 1)]
    ax.get_xaxis().set_ticks(tick_x_minor_list, minor=True)

    ax.get_xaxis().set_ticklabels(str(year) for year in range(DATE_START.year, DATE_END.year + 1))

    ax.set_xlim(get_month_delta(DATE_START), get_month_delta(DATE_END))
    ax.set_ylim(-1000, 40000)

    plt.grid(True, "major", "y")
    plt.show()

if __name__ == "__main__":
    main()
