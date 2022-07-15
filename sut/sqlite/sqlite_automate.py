import os
import sqlite3
import subprocess
from os.path import abspath, join
from time import sleep

from utils import parse_utf, print

IN_DIR = "../results/polluted_files_csv/"
OUT_DIR = "../results/loading/sqlite/"

CREATE_DEFAULT_TABLE = (
    "CREATE TABLE `table1` ("
    "  `date` date,"
    "  `time` time,"
    "`Qty` integer ,"
    "  `product_id` char(7) NOT NULL,"
    "  `Price` decimal(4,2) ,"
    "`ProductType` varchar(255) ,"
    "`ProductDescription` varchar(2048) ,"
    "`Url` varchar(255) ,"
    "`Comments` varchar(255) ,"
    "  PRIMARY KEY (`date`,`time`,`product_id`)"
    ")")

COL_NAMES = ["date", "time", "Qty", "product_id", "Price", "ProductType", "ProductDescription", "Url", "Comments"]


def load_csv(filename, params):
    path = join(abspath(IN_DIR), filename)

    i = 0
    while i < 100:
        try:
            os.remove('benchmark.db')
            i = 100
        except PermissionError:
            sleep(0.05)
        except FileNotFoundError:
            i = 100
        i += 1

    cnx = sqlite3.connect('benchmark.db')
    cursor = cnx.cursor()

    try:
        cursor.execute("DROP TABLE table1")
    except Exception:
        pass

    out_path = join(abspath(OUT_DIR), filename + '_converted.csv')
    out_cmd = f'sqlite3 -header -csv benchmark.db "SELECT * FROM table1" > "{out_path}"'

    encoding = params['charset']
    if encoding not in ['UTF-8', 'UTF-16', 'UTF-16le', 'UTF-16be']:
        encoding = 'UTF-8'
    set_encoding_stmt = f"PRAGMA encoding = \'{encoding}\';"

    create_cmd = set_encoding_stmt + params["create_table"]

    set_mode_cmd = f'.mode csv'
    set_separator_cmd = f'.separator "{params["field_delimiter"]}" {params["record_delimiter"]}'
    import_cmd = f'.import --skip {params["preamble_rows"] + 1 - params["no_header"]} \'{path}\' table1'

    try:
        os.remove(out_path)
    except FileNotFoundError:
        pass

    try:
        cursor.executescript(create_cmd)
        subprocess.Popen(["sqlite3", "benchmark.db", set_mode_cmd, set_separator_cmd, import_cmd], stderr=subprocess.PIPE)
        # choosing _not_ to output an Application error, when some error occurred, but an output was produced

    except Exception as e:
        print("Application error on file", filename)
        print("\t", str(e)[:min(len(str(e)), 253)] + '...' if len(str(e)) > 253 else ''
              )
        with open(out_path, "w") as text_file:
            text_file.write("Application Error\n")
            text_file.write(str(e))
        return

    sleep(0.5)
    try:
        os.system(out_cmd)

    except Exception as e:
        print("\t", "Error in query:", out_cmd)
        print(e, "\n")


    escaped = filename + "_converted.csv"
    print(f'\t "{escaped}"')

    cnx.close()


benchmark_files = os.listdir(IN_DIR)
for f in benchmark_files:

    params = {"charset": "ascii",
              "field_delimiter": ",",
              "quotation_mark": '"',
              "record_delimiter": "\\n",
              "preamble_rows": 0,
              "escape_char": '"',
              "no_header": 0,
              "col_names": COL_NAMES,
              "create_table": CREATE_DEFAULT_TABLE}

    if "no_header" in f:
        params["no_header"] = 1

    elif "file_field_delimiter" in f:
        ds = parse_utf(f, "file_field_delimiter_")
        params["field_delimiter"] = ds

    elif "file_quotation_char" in f:
        qs = parse_utf(f, "file_quotation_char_")
        params["quotation_mark"] = qs

    elif "file_preamble" in f:
        params["preamble_rows"] = 2  # should we?

    load_csv(f, params)
