import json
import os
import pdb
import sqlite3
import subprocess
from os.path import abspath, join
from time import sleep
import time
import timeit
from utils import print, save_time_df, load_parameters

dataset = os.environ["DATASET"]
sut = 'sqlite'
IN_DIR = abspath(f'/{dataset}/csv/')
PARAM_DIR = abspath(f'/{dataset}/parameters')
OUT_DIR = abspath(f'/results/{sut}/{dataset}/loading/')
TIME_DIR = abspath(f'/results/{sut}/{dataset}/')

N_REPETITIONS = 3
TO_SKIP = []

times_dict = {}

benchmark_files = os.listdir(IN_DIR)
for idx,f in enumerate(benchmark_files):
    in_filepath = join(abspath(IN_DIR), f)
    out_filename = f'{f}_converted.csv'
    out_filepath = join(OUT_DIR, out_filename)

    if os.path.exists(out_filepath):
        continue
    db_param = load_parameters(join(PARAM_DIR, f'{f}_parameters.json'))

    for time_rep in list(range(N_REPETITIONS)):

        db_path = f'benchmark_{time_rep}.db'
        while os.path.isfile(db_path):
            os.remove(db_path)

        encoding = db_param['encoding']
        if encoding not in ['UTF-8', 'UTF-16', 'UTF-16le', 'UTF-16be']:
            encoding = 'UTF-8'
        set_encoding_stmt = f"PRAGMA encoding = \'{encoding}\';"

        nskip= db_param["preamble_rows"]
        set_mode_cmd = f'.mode csv'
        set_separator_cmd = f'.separator "{db_param["delimiter"]}" {db_param["record_delimiter"]}'
        import_cmd = f""".import --skip {nskip} '{in_filepath}' table1"""
        start = time.time()
        try:
            subprocess.run(["sqlite3", db_path, set_mode_cmd, set_separator_cmd, import_cmd])
            end = time.time()
            try:
                out_cmd = f'sqlite3 -header -csv benchmark_{time_rep}.db "SELECT * FROM table1" > "{out_filepath}"'
                with open(out_filepath, "w") as text_file:
                    subprocess.run(["sqlite3",  "-header", "-csv", db_path, "select * from table1"], stdout=text_file)
            except Exception as e:
                print("Error in output query: \n \t", e)
        except Exception as e:
            end = time.time()
            if not time_rep:
                print("Application error on file", f)
                print("\t", str(e))
            with open(out_filepath, "w") as text_file:
                text_file.write("Application Error\n")
                text_file.write(str(e))

        times_dict[f] = times_dict.get(f, []) + [(end - start)]

save_time_df(TIME_DIR, sut, times_dict)