import os
from importlib import reload
from os.path import abspath, join
from time import sleep

import mariadb
from mariadb import OperationalError
from utils import parse_utf, print

# import sys
# reload(sys)
# sys.setdefaultencoding('latin1')

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

IN_DIR = "../results/polluted_files_csv/"
OUT_DIR = "../results/loading/mariadb/"
DOCKER_NAME = 'mariadb-server'

TO_SKIP=[]

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
    sleep(1)
    i += 1

cursor = cnx.cursor()
CREATE_DEFAULT_TABLE = (
    "CREATE TABLE `table1` ("
    "  `date` date,"
    "  `time` time,"
    "`Qty` integer ,"
    "  `product_id` char(7) NOT NULL,"
    "  `Price` varchar(255) ,"
    "`ProductType` varchar(255) ,"
    "`ProductDescription` varchar(2048) ,"
    "`Url` varchar(255) ,"
    "`Comments` varchar(255) ,"
    "  PRIMARY KEY (`date`,`time`,`product_id`)"
    ") ENGINE=InnoDB")

COL_NAMES = ["date", "time", "Qty", "product_id", "Price", "ProductType", "ProductDescription", "Url", "Comments"]


def load_csv(filename, params):
    path = join(abspath(IN_DIR), filename)
    path = path.replace('\\', '/')
    load_stmt = f"""LOAD DATA LOCAL
    INFILE "{path}" INTO TABLE table1
    CHARACTER SET {params["charset"]} 
    FIELDS TERMINATED BY '{params["field_delimiter"]}' OPTIONALLY ENCLOSED BY '{params["quotation_mark"].replace("'", "''")}'
    LINES TERMINATED BY '{params["record_delimiter"]}'
    IGNORE {params["preamble_rows"] + 1 - params["no_header"]} LINES
    (@temp_date{", " if len(params["col_names"]) > 1 else ""}{', '.join(params["col_names"][1:])})
    set DATE = STR_TO_DATE(@temp_date,'%d/%m/%Y');
    """

    out_path = join(abspath(OUT_DIR), filename + '_converted.csv').replace('\\', '/')
    out_tmp_path = join('/tmp/', filename + '_converted.csv').replace('\\', '/')

    try:
        os.remove(out_path)
    except FileNotFoundError:
        pass
    try:
        os.remove(out_tmp_path)
    except FileNotFoundError:
        pass

    try:
        cursor.execute("DROP TABLE table1")
    except Exception:
        pass

    try:
        cursor.execute(params["create_table"])
        cursor.execute(load_stmt)

    except Exception as e:
        print("Application error on file", filename)
        print("\t", e)
        with open(out_path, "w") as text_file:
            text_file.write("Application Error\n")
            text_file.write(str(e))
        return

    out_query = f"""SELECT * from table1 INTO OUTFILE '{out_tmp_path}'
                FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' ESCAPED BY '"'
                LINES TERMINATED BY '\\r\\n';"""
    try:
        cursor.execute(out_query)
    except Exception as e:
        print("\t", "Error in query:", out_query)
        print(e, "\n")

    sleep(0.5)
    try:
        os.mkdir('/results/loading/mariadb')
    except Exception:
        pass

    copy_cmd = f'cp "{out_tmp_path}" "{out_path}"'

    os.system(copy_cmd)
    escaped = filename + "_converted.csv"
    print(f'\t "{escaped}"')


benchmark_files = os.listdir(IN_DIR)

for f in benchmark_files:
    in_filepath = join(IN_DIR, f)
    out_filename = f'{f}_converted.csv'
    out_filepath = join(OUT_DIR, out_filename)

    if f in TO_SKIP or os.path.exists(out_filepath):
        continue

    params = {"charset": "ascii",
              "field_delimiter": ",",
              "quotation_mark": '"',
              "record_delimiter": "\\r\\n",
              "preamble_rows": 0,
              "escape_char": '"',
              "no_header": 0,
              "col_names": COL_NAMES,
              "create_table": CREATE_DEFAULT_TABLE}

    if "no_header" in f:
        params["no_header"] = 1

    elif "file_field_delimiter" in f:
        ds = parse_utf(f, "file_field_delimiter_")
        # print(f"'{ds}'")
        params["field_delimiter"] = ds

    elif "file_quotation_char" in f:
        qs = parse_utf(f, "file_quotation_char_")
        # print(f"'{ds}'")
        params["quotation_mark"] = qs

    elif "file_preamble" in f:
        params["preamble_rows"] = 2  # should we?


    load_csv(f, params)
