import contextlib
from os import listdir
import os
from os.path import abspath
from os.path import join as osjoin
from utils import print, save_time_df, load_parameters
import time

# https://wiki.openoffice.org/wiki/Documentation/DevGuide/Spreadsheets/Filter_Options#Token_9.2C_csv_import
# Archive http://web.archive.org/web/20210506192110/http://wiki.openoffice.org/wiki/Documentation/DevGuide/Spreadsheets/Filter_Options
# infilter:
#   field_delimiter as ASCII code (e.g. "," is 44) or FIX.
#   For multiple character delimiters, add a / between each character's ASCII code and a final "/MRG"
#   quotation mark as ASCII code  (e.g. " is 34)
#   character set
#   first line to convert
#   cell format of columns (check webbpage for reference)

dataset = os.environ["DATASET"]
sut = 'libreoffice'
IN_DIR = abspath(f'/{dataset}/csv/')
PARAM_DIR = abspath(f'/{dataset}/parameters')
OUT_DIR = abspath(f'/results/{sut}/{dataset}/loading/')
TIME_DIR = abspath(f'/results/{sut}/{dataset}/')
TMP_DIR = abspath(f'/results/{sut}/loading/xlsx/')

N_REPETITIONS = 3
times_dict = {}

benchmark_files = listdir(IN_DIR)

for idx, f in enumerate(benchmark_files):
    in_filepath = osjoin(IN_DIR, f)
    out_filename = f'{f}_converted.csv'
    out_filepath = osjoin(OUT_DIR, out_filename)
    base_filename = os.path.splitext(f)[0]
    tmp_filepath = osjoin(TMP_DIR, base_filename + '.xlsx')

    if os.path.exists(out_filepath):
        continue
    print(f'Processing file ({idx + 1}/{len(benchmark_files)}) {f}')
    sut_param = load_parameters(osjoin(PARAM_DIR, f'{f}_parameters.json'))

    str_delimiter = sut_param["delimiter"]
    if len(str_delimiter) == 1:
        param_del = str(ord(str_delimiter))
    else:
        param_del = "/".join(map(lambda x: str(ord(x)), str_delimiter)) + "/MRG"

    str_quotechar = sut_param["quotechar"]
    param_quote = str(ord(str_quotechar[0]))  # libreoffice only accepts one quotation char

    param_charset = sut_param["encoding"].replace("-", "_")
    cmd_params = f"{param_del},{param_quote},{param_charset}"

    load_command = f'libreoffice --headless --convert-to xlsx:"Calc MS Excel 2007 XML" --infilter={cmd_params} "{in_filepath}" --outdir {TMP_DIR}'
    convert_command = f'libreoffice --headless --convert-to csv:"Text - txt - csv (StarCalc)" "{tmp_filepath}" --outdir {OUT_DIR}'

    for time_rep in range(N_REPETITIONS):
        n_rows = 0

        start = time.time()
        os.system(load_command + ">/dev/null 2>&1" + f' || echo "Application Error" > "{osjoin(OUT_DIR, f)}"')
        os.system(convert_command + ">/dev/null 2>&1")
        end = time.time()
        os.system(f"""mv "{osjoin(OUT_DIR, base_filename + ".csv")}" "{out_filepath}" """)
        with contextlib.suppress(FileNotFoundError):
            os.remove(tmp_filepath)
        times_dict[f] = times_dict.get(f, []) + [(end - start)]
        print(f'\t{f} loaded in {(end - start) * 1000} ms')

save_time_df(TIME_DIR, sut, times_dict)
print("Done")
with contextlib.suppress(FileNotFoundError):
    os.rmdir(TMP_DIR)
