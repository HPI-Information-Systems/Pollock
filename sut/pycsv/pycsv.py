import csv
from os import listdir
from os.path import abspath, join
from utils import parse_utf, print
import os

IN_DIR = abspath('./results/polluted_files_csv/')
OUT_DIR = abspath('./results/loading/pycsv/')

TO_SKIP = []

def process_file(in_filename, idx, total):
    print(f'Processing file ({idx + 1}/{total}) {in_filename}')

    in_filepath = join(IN_DIR, in_filename)

    out_filename = f'{in_filename}_converted.csv'
    out_filepath = join(OUT_DIR, out_filename)

    try:
        with open(in_filepath, newline='') as in_csvfile:
            dialect = csv.Sniffer().sniff(in_csvfile.read())
            in_csvfile.seek(0)
            reader = csv.reader(in_csvfile, dialect)
            rows = list(reader)

            with open(out_filepath, 'w', newline='') as out_csvfile:
                csv.writer(out_csvfile).writerows(rows)

    except Exception as e:
        print("Application error on file", in_filename)
        print("\t", e)
        with open(out_filepath, "w") as text_file:
            text_file.write("Application Error\n")
            text_file.write(str(e))
        return


benchmark_files = listdir(IN_DIR)

for index, f in enumerate(benchmark_files):
    in_filepath = join(IN_DIR, f)
    out_filename = f'{f}_converted.csv'
    out_filepath = join(OUT_DIR, out_filename)

    if f in TO_SKIP or os.path.exists(out_filepath):
        continue

    process_file(f, index, len(benchmark_files))
