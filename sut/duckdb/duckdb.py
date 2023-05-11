from os.path import join, abspath
import duckdb
import time
import os
from utils import print, save_time_df, load_parameters
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

sut='duckdb'
DATASET = os.environ['DATASET']
IN_DIR = abspath(f'/{DATASET}/csv/')
PARAM_DIR = abspath(f'/{DATASET}/parameters')
OUT_DIR = abspath(f'/results/{sut}/{DATASET}/loading/')
TIME_DIR = abspath(f'/results/{sut}/{DATASET}/')

N_REPETITIONS = 3

times_dict = {}
benchmark_files = os.listdir(IN_DIR)
for idx,file in enumerate(benchmark_files):
    f = os.path.basename(file)
    in_filepath = join(IN_DIR, f)
    out_filename = f'{f}_converted.csv'
    out_filepath = join(OUT_DIR, out_filename)
    sut_params = load_parameters(join(PARAM_DIR, f'{f}_parameters.json'))
    if os.path.exists(out_filepath):
        continue
    print(f"({idx}/{len(benchmark_files)}) {f}")

    for time_rep in range(N_REPETITIONS):
        kw = {}

        kw["header"]="infer"
        kw["delimiter"] = None # this means is automatically inferred
        kw["encoding"] = sut_params["encoding"]

        if sut_params["quotechar"] != '"':
            quote = sut_params["quotechar"]
            if quote:
                quote = quote[0]
            kw["quotechar"]= quote

        if sut_params["escapechar"] != sut_params["quotechar"]:
            escape = sut_params["escapechar"]
            if escape:
                escape = escape[0]
            kw["escapechar"] = escape or None
            kw["doublequote"] = False
        else:
            kw["escapechar"] = None
            kw["doublequote"] = True

        if sut_params["record_delimiter"] != "\r\n":
            rowdel = sut_params["record_delimiter"]
            rowdel = rowdel[0] if rowdel else None
            kw["lineterminator"] = rowdel

        preamble = int(sut_params["preamble_rows"])
        if int(sut_params["preamble_rows"]) != 0:
            kw["skiprows"] = preamble
        con = duckdb.connect()
        start = time.time()
        try:
            rel = con.from_query(f"SELECT * from read_csv('{in_filepath}', ignore_errors=true)")
            end = time.time()
            rel.write_csv(out_filepath, index=False)
        except Exception as e:
            end = time.time()
            print("\t", e)
            with open(out_filepath, "w") as text_file:
                text_file.write("Application Error\n")
                text_file.write(str(e))

        times_dict[f] = times_dict.get(f, []) + [(end - start)]

        try:
            del start, end, df, text_file
        except:
            pass

save_time_df(TIME_DIR, sut, times_dict)
