# sieve as a Pollock system under test. Adapted from Pollock's sut/pycsv/pycsv.py
# (https://github.com/HPI-Information-Systems/Pollock), MIT License,
# Copyright (c) 20222 Gerardo Vitagliano (Pollock's LICENSE file; a copy is kept as
# sut/LICENSE-Pollock in https://github.com/KenWuqianghao/sieve).
from os import listdir
import os
from os.path import abspath, join
from utils import print, save_time_df
import csv
import time

import sieve

sut = 'sieve'
DATASET = os.environ['DATASET']
IN_DIR = abspath(f'/{DATASET}/csv/')
OUT_DIR = abspath(f'/results/{sut}/{DATASET}/loading/')
TIME_DIR = abspath(f'/results/{sut}/{DATASET}/')
N_REPETITIONS = 3

# Unlike the other SUT scripts, this one does not call load_parameters: sieve is given nothing
# but the path of the file. Encoding, delimiter, quote, escape, header, preamble and column
# names are all detected from the file's bytes. (The path is only used to open the file.)

os.makedirs(OUT_DIR, exist_ok=True)

times_dict = {}
benchmark_files = listdir(IN_DIR)

for idx, f in enumerate(benchmark_files):
    in_filepath = join(IN_DIR, f)
    out_filename = f'{f}_converted.csv'
    out_filepath = join(OUT_DIR, out_filename)
    if os.path.exists(out_filepath):
        continue
    print(f'Processing file ({idx + 1}/{len(benchmark_files)}) {f}')

    for time_rep in range(N_REPETITIONS):
        start = time.time()
        try:
            rows = sieve.load(in_filepath)
            end = time.time()
            with open(out_filepath, 'w', newline='', encoding='utf-8') as out_csvfile:
                csv.writer(out_csvfile).writerows(rows)

        except Exception as e:
            end = time.time()
            print("Application error on file", f)
            print("\t", e)
            with open(out_filepath, "w") as out_csvfile:
                out_csvfile.write("Application Error\n")
                out_csvfile.write(str(e))

        times_dict[f] = times_dict.get(f, []) + [(end - start)]

        try:
            del start, end, rows, out_csvfile
        except:
            pass

save_time_df(TIME_DIR, sut, times_dict)
