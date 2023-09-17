
import csv
import os.path
from os import path, mkdir
import json
import shutil

with open("./data/account_001/statement_list.csv", "r") as f_stat_src:

    r = csv.DictReader(f_stat_src)

    for stat_src in r:

        print(stat_src)

        if stat_src["name"] == "pending":
            print("skipped")
            continue

        stat_dst_name = stat_src["date"][:7]

        if path.exists(f"./data_2/wallet_main/account_ce_live/stat_{stat_dst_name}"):
            print("skipped")
            continue

        print("processing src stat %s", stat_src["date"][:7])
        print("creating dst stat %s", stat_dst_name)

        stat_dst_path = f"./data_2/wallet_main/account_ce_live/stat_{stat_dst_name}"
        print(f"mkdir {stat_dst_path}")
        os.mkdir(stat_dst_path)

        stat_dst_info_data = {
            "name": stat_dst_name,
            "date": f"{stat_dst_name}-19",
            "bal_start": float(stat_src["bal_start"]),
            "bal_end": float(stat_src["bal_end"])
        }

        json_string = json.dumps(stat_dst_info_data)

        stat_dst_info_file_path = f"{stat_dst_path}/info.json"

        print("write %s to %s" % (json_string, stat_dst_info_file_path))
        with open(stat_dst_info_file_path, "w") as f_stat_dst:
          json.dump(stat_dst_info_data, f_stat_dst)

        stat_src_ope_list_file_path = "./data/account_001/statement_%03d/operation_list.csv" % int(stat_src['id'])
        stat_dst_ope_list_file_path = f"./data_2/wallet_main/account_ce_live/stat_{stat_dst_name}/ope_list.csv"

        print("copy %s to %s" % (stat_src_ope_list_file_path, stat_dst_ope_list_file_path))
        shutil.copyfile(stat_src_ope_list_file_path, stat_dst_ope_list_file_path)
