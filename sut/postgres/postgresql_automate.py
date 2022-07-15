import os
from os.path import abspath, join
from time import sleep

from psycopg2 import OperationalError
from utils import parse_utf
import psycopg2

IN_DIR = abspath("../results/polluted_files_csv/")
OUT_DIR = abspath("../results/loading/postgres/")

host = 'postgres-server'

i = 0
done = False
cnx = None
while i < 120 and not done:
    try:
        cnx = psycopg2.connect(
            user="benchmark",
            password="benchmark",
            host=host,
            database="benchmark"
        )
        done = True
        print('Connected')
    except OperationalError as e:
        print(e)
        if i >= 119:
            quit(1)
    print('Waiting for server...')
    sleep(1)
    i += 1

cnx.autocommit = True
cursor = cnx.cursor()
CREATE_DEFAULT_TABLE = (
    "CREATE TABLE table1 ("
    "date date,"
    "time time,"
    "Qty integer ,"
    "product_id char(7) NOT NULL,"
    "Price money,"
    "ProductType varchar(255) ,"
    "ProductDescription varchar(2048) ,"
    "Url varchar(255),"
    "Comments varchar(255),"
    "  PRIMARY KEY (date, time,product_id)"
    ")")

COL_NAMES = ["date", "time", "Qty", "product_id", "Price", "ProductType", "ProductDescription", "Url", "Comments"]


def configure_date_style():
    set_date_style = 'set datestyle = euro;'
    cursor.execute(set_date_style)


def load_csv(filename, kw):
    path = join(IN_DIR, filename)

    load_stmt = f"""
    COPY table1
    FROM '{path}'
    CSV
    ENCODING '{kw["charset"]}' 
    DELIMITER '{kw["field_delimiter"]}'
    QUOTE '{kw["quotation_mark"].replace("'", "''")}'
    FORCE NULL {", ".join(n for n in kw["col_names"])}
    {'HEADER' if not kw["no_header"] else ''}
    ESCAPE '{kw["escape_char"]}';
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
        cursor.execute(kw["create_table"])
        cursor.execute(load_stmt)

    except Exception as e:
        print(f"\033[31mApplication error on file {filename}")
        print("\t", e)
        with open(join(OUT_DIR, filename + "_converted.csv"), "w") as text_file:
            text_file.write("Application Error\n")
            text_file.write(str(e))
        return

    out_query = f"""
                COPY table1
                TO '{out_tmp_path}'
                CSV
                DELIMITER ','
                QUOTE '"'
                ESCAPE '"';"""
    try:
        cursor.execute(out_query)

    except Exception as e:
        print("\t", "Error in query:", out_query)
        print(e, "\n")

    sleep(0.5)
    try:
        os.mkdir('/results/loading/postgres')
    except Exception:
        pass

    copy_cmd = f'cp "{out_tmp_path}" "{out_path}"'
    os.system(copy_cmd)


    escaped = filename + "_converted.csv"
    print(f'\t Converted: "{escaped}"')


def main():
    benchmark_files = os.listdir(IN_DIR)

    for f in benchmark_files:
        print(f'\033[96mProcessing file: {f}')

        kw = {"charset": "UTF8",
              "field_delimiter": ",",
              "quotation_mark": '"',
              "escape_char": '"',
              "no_header": 0,
              "col_names": COL_NAMES,
              "create_table": CREATE_DEFAULT_TABLE}

        if "no_header" in f:
            kw["no_header"] = 1
        elif "file_field_delimiter" in f:
            ds = parse_utf(f, "file_field_delimiter_")
            kw["field_delimiter"] = ds
        elif "file_quotation_char" in f:
            qs = parse_utf(f, "file_quotation_char_")
            kw["quotation_mark"] = qs

        load_csv(f, kw)


configure_date_style()

if __name__ == '__main__':
    main()
