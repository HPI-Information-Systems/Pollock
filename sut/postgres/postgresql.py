import contextlib
import os
from os.path import abspath, join
from time import sleep
import time

from psycopg2 import OperationalError
from utils import print, save_time_df, load_parameters
import psycopg2

def connect_to_db():
    HOST = 'postgres-server'
    i = 0
    done = False
    cnx = None
    while i < 120 and not done:
        try:
            cnx = psycopg2.connect(
                user="benchmark",
                password="benchmark",
                host=HOST,
                database="benchmark"
            )
            done = True
            print('Connected')
        except OperationalError as e:
            print(e)
            if i >= 119:
                quit(1)
        print('Waiting for server...')
        sleep(0.5)
        i += 1
    if not done:
        raise Exception('Could not connect to server')
    return cnx

dataset = os.environ['DATASET']
sut='postgres'
IN_DIR = abspath(f'/{dataset}/csv/')
PARAM_DIR = abspath(f'/{dataset}/parameters')
OUT_DIR = abspath(f'/results/{sut}/{dataset}/loading/')
TIME_DIR = abspath(f'/results/{sut}/{dataset}/')

N_REPETITIONS = 3

times_dict = {}
cnx = connect_to_db()
cnx.autocommit = True


benchmark_files = os.listdir(IN_DIR)
for idx,f in enumerate(benchmark_files):
    in_filepath = join(IN_DIR, f).replace('\\', '/')
    out_filename = f'{f}_converted.csv'
    out_filepath = join(OUT_DIR, out_filename).replace('\\', '/')
    out_tmp_path = join('/tmp/', f + '_converted.csv').replace('\\', '/')

    if os.path.exists(out_filepath):
        continue
    print(f'({idx + 1}/{len(benchmark_files)}) {f}')

    db_param = load_parameters(join(PARAM_DIR, f'{f}_parameters.json'))
    db_param["encoding"] = "UTF8" if db_param["encoding"] == "ascii" else db_param["encoding"]

    create_stmt = "CREATE TABLE table1 (pk int GENERATED ALWAYS AS IDENTITY PRIMARY KEY, "
    for c in db_param["column_names"]:
        create_stmt += f'"{c}" varchar(65535),'
    create_stmt = create_stmt[:-1] + ")"


    load_stmt = f"""COPY table1( {",".join(f'"{c}"' for c in db_param["column_names"])})
FROM '{in_filepath}' CSV
ENCODING '{db_param["encoding"]}' 
DELIMITER '{db_param["delimiter"]}'
QUOTE '{db_param["quotechar"].replace("'", "''")}' FORCE NULL 
"{'", "'.join(n for n in db_param["column_names"])}"
{'HEADER' if not db_param["no_header"] else ' '};"""

    if db_param["escapechar"]:
        load_stmt = load_stmt[:-1] + f""" ESCAPE '{db_param["escapechar"]}'"""

    for time_rep in list(range(N_REPETITIONS)):
        cursor = cnx.cursor()

        with contextlib.suppress(FileNotFoundError):
            os.remove(out_filepath)
            os.remove(out_tmp_path)

        try:
            cursor.execute("DROP TABLE table1")
        except Exception:
            pass

        start = time.time()
        try:
            cursor.execute(create_stmt)
            cursor.execute(load_stmt)
            end = time.time()

            out_query = f"COPY table1("
            out_query += ",".join(f'"{c}"' for c in db_param["column_names"])
            out_query+= f""") TO '{out_filepath}' CSV DELIMITER ',' QUOTE '"' ESCAPE '"' HEADER;"""
            try:
                cursor.execute(out_query)
            except Exception as e:
                print("\t", "Error in output query:", out_query)
                print(e, "\n")

        except Exception as e:
            end = time.time()
            if not time_rep:
                print("\033[91m {}\033[00m".format("Application Error on file:" + f))
                print("\033[91m {}\033[00m".format(f"\t{e}"))
            with open(out_filepath, "w") as text_file:
                text_file.write("Application Error\n")
                text_file.write(str(e))

        times_dict[f] = times_dict.get(f, []) + [(end - start)]

save_time_df(TIME_DIR, sut, times_dict)
