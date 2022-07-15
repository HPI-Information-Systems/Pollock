from os.path import join

import pandas as pd
import os
from utils import parse_utf

"""
(filepath_or_buffer, 
delimiter=None, Delimiter to use. If sep is None, the Python parsing engine will be used and automatically detect the separator.
            In addition, separators longer than 1 character and different from '\s+' will be interpreted as regex. 
            Note that regex delimiters are prone to ignoring quoted data. Regex example: '\r\t'.
header='infer', Row number(s) to use as the column names, and the start of the data. 
prefix=None, 
mangle_dupe_cols=True, 
skipinitialspace=False, 
skiprows=None, Line numbers to skip (0-indexed) or number of lines to skip (int) at the start of the file.
skipfooter=0, Number of lines at bottom of file to skip 
nrows=None, 
na_values=None, 
keep_default_na=True, 
na_filter=True,
skip_blank_lines=True, 
parse_dates=False, 
infer_datetime_format=False, 
keep_date_col=False, 
date_parser=None, 
dayfirst=False,
thousands=None, 
decimal='.', 
quotechar='"',
doublequote=True, 
escapechar=None, 
comment=None, 
encoding=None, 
error_bad_lines=True, 
warn_bad_lines=True,
low_memory=True"""

IN_DIR = "/results/polluted_files_csv/"
OUT_DIR = "/results/loading/pandas/"

TO_SKIP = []

def load_csv(filename, *args, **kwargs):
    try:
        # Pandas does weird inference when not dtype=object, check row_field_delimiter files
        df = pd.read_csv(IN_DIR + filename, dtype=object, on_bad_lines='skip', *args, **kwargs)
    except Exception as e:
        print(filename)
        print("\t", e)
        with open(OUT_DIR + filename + "_converted.csv", "w") as text_file:
            text_file.write("Application Error\n")
            text_file.write(str(e))
        return

    df.to_csv(join(OUT_DIR, filename + "_converted.csv"), index=False)


benchmark_files = os.listdir(IN_DIR)

for f in benchmark_files:
    in_filepath = join(IN_DIR, f)
    out_filename = f'{f}_converted.csv'
    out_filepath = join(OUT_DIR, out_filename)

    if f in TO_SKIP or os.path.exists(out_filepath):
        continue

    kw = {}

    if "no_header" in f:
        kw = {"header": None}

    elif "file_field_delimiter" in f:
        ds = parse_utf(f, "file_field_delimiter_")
        # print(f"'{ds}'")
        kw = {"delimiter": ds}

    elif "file_quotation_char" in f:
        qs = parse_utf(f, "file_quotation_char_")
        # print(f"'{ds}'")
        kw = {"quotechar": qs}

    elif "file_preamble" in f:
        kw = {"skiprows": 2}  # should we?

    load_csv(f, **kw)
