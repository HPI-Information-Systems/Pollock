import pdb
from os import listdir
import os
from os.path import abspath
from os.path import join as osjoin
from utils import print, save_time, parse_utf
import time


#https://wiki.openoffice.org/wiki/Documentation/DevGuide/Spreadsheets/Filter_Options#Token_9.2C_csv_import
#Archive http://web.archive.org/web/20210506192110/http://wiki.openoffice.org/wiki/Documentation/DevGuide/Spreadsheets/Filter_Options
#infilter:
#   field_delimiter as ASCII code (e.g. "," is 44) or FIX.
#   For multiple character delimiters, add a / between each character's ASCII code and a final "/MRG"
#   quotation mark as ASCII code  (e.g. " is 34)
#   character set
#   first line to convert
#   cell format of columns (check webbpage for reference)

IN_DIR = abspath('./results/polluted_files_csv/')
OUT_DIR = abspath('/app/results/loading/libreoffice/')
TMP_DIR = abspath('/app/results/loading/libreoffice/xlsx/')
TIME_DIR = abspath('/app/results/time/libreoffice/')
N_REPETITIONS = 3
TO_SKIP=[]

def process_file(in_filename, idx, total):
    print(f'Processing file ({idx + 1}/{total}) {in_filename}')
    in_filepath = osjoin(IN_DIR, in_filename)
    out_filename = f'{in_filename}_converted.csv'
    out_filepath = osjoin(OUT_DIR, out_filename)
    base_filename = os.path.splitext(in_filename)[0]
    tmp_filepath = osjoin(TMP_DIR,base_filename+'.xlsx')

    for time_rep in range(N_REPETITIONS):
        time_filename = f'{in_filename}_time_{time_rep}.csv'
        time_filepath = osjoin(TIME_DIR, time_filename)

        n_rows = 0
        if "file_field_delimiter" in base_filename:
            str_delimiter=parse_utf(in_filename, "file_field_delimiter_")
            if len(str_delimiter) == 1:
                parameters = str(ord(str_delimiter))+",34,UTF-8"
            else:
                parameters = "/".join(map(lambda x: str(ord(x)), str_delimiter))+"/MRG,34,UTF-8"
        elif "file_quotation_char" in base_filename:
            str_quotechar=parse_utf(in_filename, "file_quotation_char_")
            parameters = "44,"+str(ord(str_quotechar[0]))+",UTF-8" #libreoffice only accepts one quotation char
        else:
            parameters = "44,34,UTF-8"

        load_command = f'libreoffice --headless --convert-to xlsx:"Calc MS Excel 2007 XML" --infilter={parameters} {in_filepath} --outdir {TMP_DIR}'
        convert_command = f'libreoffice --headless --convert-to csv:"Text - txt - csv (StarCalc)" {tmp_filepath} --outdir {OUT_DIR}'

        start = time.time()
        os.system(load_command + ">/dev/null 2>&1" +f' || echo "Application Error" > "{out_filepath}"')
        os.system(convert_command + ">/dev/null 2>&1")
        os.system(f"mv {osjoin(OUT_DIR,in_filename)} {out_filepath}")
        end = time.time()
        save_time(time_filepath, end - start, n_rows)
        os.remove(tmp_filepath)


benchmark_files = listdir(IN_DIR)

for index, f in enumerate(benchmark_files):
    out_filename = f'{f}_converted.csv'
    out_filepath = osjoin(OUT_DIR, out_filename)

    if f in TO_SKIP or os.path.exists(out_filepath):
        continue
    process_file(f, index, len(benchmark_files))

print("Done")
try:
    os.rmdir(TMP_DIR)
except:
    pass
