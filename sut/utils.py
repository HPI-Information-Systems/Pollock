import json
import builtins as __builtin__
from datetime import datetime
from time import time
from pathlib import Path
import pandas as pd

def parse_utf(filename, pollution):
    """
    Convenience function to split for example "table_field_delimiter_0x20.csv" into the string "," to feed as a parameter.
    :param filename: the filename containing a pollution, a set of unicode characters in hex-string form delimited with underscore
    :param pollution: the pollution to isolate
    :return: the string joined parsing the utf characters
    """
    arr = filename.split(pollution)[1][:-4]
    s = "".join([chr(int(d, 0)) for d in arr.split("_")])
    if s == "\x00":
        return ""
    return s


def print(*args, **kwargs):
    """
    Custom print functions that outputs the timestamp (in local computer time)
    :param args:
    :param kwargs:
    :return:
    """
    return __builtin__.print(f'\033[94m{datetime.fromtimestamp(time() + 3600).strftime("%H:%M:%S")}:\033[0m', flush=True, *args, **kwargs)


def save_time(time_path, time, n_rows):
    """
    Save the time in a file
    :param time_path: the path of the file
    :param time: the time to save
    :param n_rows: the number of rows
    :return:
    """
    Path(time_path).parent.mkdir(parents=True, exist_ok=True)
    with open(time_path, "w") as time_file:
        str_time = f"time,{time}"
        str_time += f"\nn_rows,{n_rows}"
        time_file.write(str_time)


def save_time_df(TIME_DIR, sut, times_dict):
    if not times_dict:
        print("No time changes to update")
        return
    N_REPETITIONS = len(times_dict[list(times_dict.keys())[0]])
    update_time_df = pd.DataFrame.from_dict(times_dict, orient="index", columns=[f"{sut}_time_{i}" for i in range(N_REPETITIONS)])
    try:
        sut_time_df = pd.read_csv(f'{TIME_DIR}/{sut}_time.csv', index_col='filename')
        sut_time_df = pd.concat([sut_time_df, update_time_df]).groupby(level=0).last()
    except FileNotFoundError:
        sut_time_df = update_time_df
    sut_time_df.to_csv(f'{TIME_DIR}/{sut}_time.csv', index_label='filename')


def load_parameters(parameters_file, for_sql=False):
    with open(parameters_file, "r") as jf:
        params = json.load(jf)
    if params["column_names"]:
        col_names = [x.strip() for x in params["column_names"]]
    else:
        if params["n_columns"] > 0:
            col_names = [f'col_{i}' for i in range(int(params["n_columns"]))]
        else:
            col_names = ["col_0"]

    if for_sql:
        if params["encoding"] == "ascii":
            params["encoding"] = "UTF8" 
        params["encoding"] = params["encoding"].replace("-", "")
        params["quotechar"] = params["quotechar"].replace("'", "''")
        params["escapechar"] = params["escapechar"].replace("'", "''")

    return {"encoding": params["encoding"],
            "delimiter": params["delimiter"] or ',',
            "quotechar": params["quotechar"] or '"',
            "escapechar": params["escapechar"] or '"',
            "record_delimiter": params["row_delimiter"],
            "header_lines": int(params["header_lines"]),
            "preamble_rows": int(params["preamble_lines"]),
            "no_header": int(int(params["header_lines"]) == 0),
            "column_names": col_names}
