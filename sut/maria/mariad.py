import contextlib
import os
from os.path import abspath, join
from pathlib import Path
from time import sleep

import mariadb
from mariadb import OperationalError
from utils import print, save_time_df, load_parameters
import time

"""
LOAD DATA [LOW_PRIORITY | CONCURRENT] [LOCAL] INFILE 'file_name'
    [REPLACE | IGNORE]
    INTO TABLE tbl_name
    [CHARACTER SET charset_name]
    [{FIELDS | COLUMNS}
        [TERMINATED BY 'string']
        [[OPTIONALLY] ENCLOSED BY 'char']
        [ESCAPED BY 'char']
    ]
    [LINES
        [STARTING BY 'string']
        [TERMINATED BY 'string']
    ]
    [IGNORE number LINES]
    [(col_name_or_user_var,...)]
    [SET col_name = expr,...]
    """


def connect_to_db():
    HOST = 'mariadb-server'
    i = 0
    done = False
    cnx = None
    while i < 120 and not done:
        try:
            cnx = mariadb.connect(user='root', password='benchmark', host=HOST, port=3307, database='benchmark',
                                  local_infile=True)
            done = True
            print('Connected')
        except OperationalError as e:
            if i >= 119:
                quit(1)
        print('Waiting for server...')
        sleep(0.5)
        i += 1
    if not done:
        raise Exception('Could not connect to server')
    return cnx


dataset = os.environ["DATASET"]
sut = 'mariadb'
IN_DIR = abspath(f'/{dataset}/csv/')
PARAM_DIR = abspath(f'/{dataset}/parameters')
OUT_DIR = abspath(f'/results/{sut}/{dataset}/loading/')
TIME_DIR = abspath(f'/results/{sut}/{dataset}/')

N_REPETITIONS = 3

times_dict = {}
cnx = connect_to_db()

benchmark_files = os.listdir(IN_DIR)
for idx, f in enumerate(benchmark_files):

    in_filepath = join(IN_DIR, f).replace('\\', '/')
    out_filename = f'{f}_converted.csv'
    out_filepath = join(OUT_DIR, out_filename).replace('\\', '/')
    out_tmp_header_path = join('/tmp/', f + '_header.csv').replace('\\', '/')
    out_tmp_data_path = join('/tmp/', f + '_data.csv').replace('\\', '/')

    if os.path.exists(out_filepath):
        continue
    print(f'({idx + 1}/{len(benchmark_files)}) {f}')

    db_param = load_parameters(join(PARAM_DIR, f'{f}_parameters.json'), for_sql=True)

    create_stmt = "CREATE TABLE `table1` ( pk INT NOT NULL AUTO_INCREMENT,"
    for c in db_param["column_names"]:
        create_stmt += f"`{c}` TEXT,"
    create_stmt += " PRIMARY KEY (pk)) ENGINE=InnoDB"

    load_stmt = f"""LOAD DATA LOCAL INFILE "{in_filepath}" INTO TABLE table1 
CHARACTER SET {db_param["encoding"]}
FIELDS TERMINATED BY '{db_param["delimiter"]}' 
OPTIONALLY ENCLOSED BY '{db_param["quotechar"]}'
ESCAPED BY '{db_param["escapechar"]}'
LINES TERMINATED BY '{db_param["record_delimiter"]}'
IGNORE {db_param["preamble_rows"] + 1 - db_param["no_header"]} LINES 
(`{'`, `'.join(db_param["column_names"])}`);
"""

    for time_rep in list(range(N_REPETITIONS)):
        with contextlib.suppress(FileNotFoundError):
            os.remove(out_filepath)

        cursor = cnx.cursor()
        try:
            cursor.execute('DROP TABLE table1')
        except Exception:
            pass

        start = time.time()
        try:
            cursor.execute(create_stmt)
            cursor.execute(load_stmt)
            end = time.time()

            out_query_header = f"""select GROUP_CONCAT(CONCAT('"',COLUMN_NAME,'"') order BY ORDINAL_POSITION) 
from INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'table1' AND COLUMN_NAME != 'pk'
INTO OUTFILE '{out_tmp_header_path}'
FIELDS TERMINATED BY ',' ESCAPED BY '' LINES TERMINATED BY '\\r\\n';"""
            out_query_data = f"""SELECT {",".join(f'`{c}`' for c in db_param["column_names"])} from table1 INTO OUTFILE '{out_tmp_data_path}' FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' ESCAPED BY '"' LINES TERMINATED BY '\\r\\n';"""
            Path(OUT_DIR).mkdir(parents=True, exist_ok=True)
            with contextlib.suppress(FileNotFoundError):
                os.remove(out_tmp_header_path)
                os.remove(out_tmp_data_path)
            try:
                cursor.execute(out_query_header)
                cursor.execute(out_query_data)
            except Exception as err:
                print("\t", "Error in output query:", out_query_data)
                print(err, "\n")
            os.system(f"cat '{out_tmp_header_path}' '{out_tmp_data_path}' > '{out_filepath}'")

        except Exception as e:
            end = time.time()
            if not time_rep:
                print("\033[91m {}\033[00m".format("Application Error on file:" + f))
                print("\033[91m {}\033[00m".format(f"\t{e}"))
            with open(out_filepath, "w") as text_file:
                text_file.write("Application Error\n")
                text_file.write(str(e))

        if time_rep in range(N_REPETITIONS):
            times_dict[f] = times_dict.get(f, []) + [(end - start)]
            print(f'\t{f} loaded in {(end - start) * 1000} ms')

save_time_df(TIME_DIR, sut, times_dict)
