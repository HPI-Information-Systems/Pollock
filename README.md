# Pollock
Pollock is a benchmark for data loading on character-delimited files, developed at the Information Systems Group of the Hasso Plattner Institute.

## Setup

The code is written using Python 3.8.5.
If using a local (or virtual) environment, install dependencies with
`pip install -r requirements.txt`
Alternatively, if using a conda distribution on Linux, use:
`conda env create --file pollock.yml`

## Benchmark files
For the complete list of benchmark files, expand the following table.
<details>
<summary>Pollock files</summary>

|Pollution level | File name | Pollution type|
|-------------------|-----------|-----------|
|Standard file | source.csv | Standard file|
|File name| source | File name without extension|
| |" "| File name is a single breaking space, without extension|
| |" .csv" | File name is a single breaking space|
| |".csv"  | File name with the only extension|
| |"source.tsv"| File name with the incorrect extension, suggesting plain-text data|
| |"source.pdf"| File name with the incorrect extension, suggesting binary file |
| |"source.loremipsumdolor"| File name with the incorrect extension, arbitrary|
|File dimension| "file_dimension_0.csv" | Empty file, with a dimension of 0 bytes|
| | "file_dimension_200.csv"| Very small file, with a dimension of 200 bytes|
| | "file_dimension_1500000000.csv" | Very large file, with a dimension of 1.39GB |
|File encoding | "file_encoding_latin_1.csv" | File encoded with latin-1 encoding.|
| | "file_encoding_utf_16.csv" | File encoded with utf-16 encoding. |
| | "file_encoding_utf_8.csv" | File encoded with utf-8 encoding|
|Number of tables | "table_multitable_rows_10_less_cols.csv"| File with two tables, the first with 10 rows and less columns than the second, with no empty line to separate them.|
| |"table_multitable_rows_10_less_cols_separated.csv" |File with two tables, the first with 10 rows and less columns than the second, with an empty line to separate them. |
| |"table_multitable_rows_10_more_cols.csv"| File with two tables, the second with 10 rows and more columns than the first, with no empty line to separate them. |
| |"table_multitable_rows_10_more_cols_separated.csv" | File with two tables, the second with 10 rows and more columns than the first, with an empty line to separate them.  |
|Number of columns |"table_num_columns_1.csv" | File with a single column|
| |"table_num_columns_1024.csv"| File with 1024 columns|
| |"table_num_columns_17000.csv" | File with 17000 columns|
|Number of rows |"table_num_rows_1.csv"|File with a single row|
| |"table_num_rows_70000.csv"|File with 70000 rows|
| |"table_num_rows_99_no_header.csv" | File with 99 rows but no header|
|Metadata rows |"table_preamble_3_delimited.csv" | File with three preamble rows, delimited, not separated from the table|
| |"table_preamble_3_delimited_empty_row.csv" | File with three preamble rows, delimited, separated from the table with an empty row|
| |"table_preamble_3_not_delimited.csv" | File with three preamble rows, not delimited, not separated from the table.|
| |"table_preamble_3_not_delimited_empty_row.csv" | File with three preamble rows, not delimited separated from the table with an empty row|
| |"table_footnote_3_delimited.csv" | File with three footnote rows, delimited, not separated from the table|
| |"table_footnote_3_delimited_empty_row.csv" | File with three footnote rows, delimited, separated from the table with an empty row|
| |"table_footnote_3_not_delimited.csv" | File with three footnote rows, not delimited, not separated from the table.|
| |"table_footnote_3_not_delimited_empty_row.csv" | File with three footnote rows, not delimited separated from the table with an empty row|
|Dialect | "table_record_delimiter_0xA.csv"| File where rows end with the LF character.|
| |"table_record_delimiter_0xD.csv" | File where rows end with the CR character.|
| |"table_record_delimiter_0xD_0xA.csv" | File where rows end with the CRLF sequence |
||table_field_delimiter_0x20.csv| File where fields are delimited with space
||table_field_delimiter_0x2C.csv| File where fields are delimited with comma
||table_field_delimiter_0x2C_0x20.csv| File where fields are delimited with comma and space
||table_field_delimiter_0x3A.csv| File where fields are delimited with colon
||table_field_delimiter_0x3B.csv| File where fields are delimited with semicolon
||table_field_delimiter_0x5C_0x74.csv| File where fields are delimited with the "\t" sequence
||table_field_delimiter_0x7C.csv| File where fields are delimited with the pipe symbol
||table_field_delimiter_0x9.csv| File where fields are delimited with tab
||table_field_delimiter_0x9_0x9.csv| File where fields are delimited with double tab
||table_quotation_char_0x22.csv| File where the quotation character is the double quote character
||table_quotation_char_0x22_0x20.csv| File where the quotation character is the sequence of double quote and space
||table_quotation_char_0x27.csv| File where the quotation character is the apostrophe
||table_escape_char_0x22_0x22.csv| File where the escape character is the sequence of two double quotes
||table_escape_char_0x5C.csv| File where the escape character is the backslash
|Row Structure|row_n_fields_1_empty.csv| File where the header row is empty
||row_n_fields_1_less.csv| File where the header row has less fields than the others
||row_n_fields_1_more.csv| File where the header row has more fields than the others
||row_n_fields_2_empty.csv| File where the first data row is empty
||row_n_fields_2_less.csv| File where the first data row has less fields than the others
||row_n_fields_2_more.csv| File where the first data row has more fields than the others
||row_n_fields_50_empty.csv| File where the 50th data row is empty
||row_n_fields_50_less.csv| File where the 50th data row has less fields than the others
||row_n_fields_50_more.csv| File where the 50th data row has more fields than the others
||row_n_fields_last()-0_empty.csv| File where the last data row is empty
||row_n_fields_last()-0_less.csv|File where the last data row has less fields than the others
||row_n_fields_last()-0_more.csv|File where the last data row has more fields than the others
|Row Dialect|row_record_delimiter_1_0xA.csv| File where only the header row ends with the LF character
||row_record_delimiter_2_0xA.csv|File where only the first data row ends with the LF character
||row_record_delimiter_50_0xA.csv| File where only the 50th row ends with the LF character
||row_record_delimiter_last()-0_0xA.csv| File where only the last row ends with the LF character
||row_field_delimiter_1_0x3B.csv| File where only the header row is delimited with semicolon
||row_field_delimiter_2_0x3B.csv| File where only the first data row is delimited with semicolon
||row_field_delimiter_50_0x3B.csv| File where only the 50th row is delimited with semicolon
||row_field_delimiter_last()-0_0x3B.csv| File where only the last row is delimited with semicolon
||row_quotation_mark_1_0x27.csv| File where only the header row is quoted with apostrophe
||row_quotation_mark_2_0x27.csv| File where only the first data row is quoted with apostrophe
||row_quotation_mark_50_0x27.csv| File where only the 50th row is quoted with apostrophe
||row_quotation_mark_last()-0_0x27.csv| File where only the last row is quoted with apostrophe
||row_escape_char_1_0x5C.csv| File where only the header row is escaped with backslash
||row_escape_char_2_0x5C.csv| File where only the first data row is escaped with backslash
||row_escape_char_50_0x5C.csv| File where only the 50th row is escaped with backslash
||row_escape_char_last()-0_0x5C.csv| File where only the last row is escaped with backslash
|Column Header|column_header_[1, 2]_regular_nonunique.csv| File where the first two columns have the same header
||column_header_1_empty_nonalnum.csv| File where the first column header is empty
||column_header_1_large.csv| File where the first column header is larger than 255 characters
||column_header_1_regular_multiple.csv| File where the first column header spans multiple rows
||column_header_1_regular_nonalnum.csv| File where the first column header contains the percentage symbol
||column_header_3_empty_nonalnum.csv|File where the 3rd column header is empty
||column_header_3_large.csv|File where the 3rd column header is larger than 255 characters
||column_header_3_regular_multiple.csv|File where the 3rd column header spans multiple rows
||column_header_3_regular_nonalnum.csv|File where the 3rd column header contains the percentage symbol
||column_header_last()-0_empty_nonalnum.csv|File where the last column header is empty
||column_header_last()-0_large.csv|File where the last column header is larger than 255 characters
||column_header_last()-0_regular_multiple.csv|File where the last column header spans multiple rows
||column_header_last()-0_regular_nonalnum.csv|File where the last column header contains the percentage symbol
|Column Format|column_heterogeneous_format_col1_row_-1.csv|
||column_heterogeneous_format_col1_row_2.csv|
||column_heterogeneous_format_col1_row_50.csv|
||column_heterogeneous_format_col1_row_range(1, 50).csv|
||column_heterogeneous_format_col1_row_range(30, 80).csv|
||column_heterogeneous_format_col1_row_range(50, 100).csv|
||column_heterogeneous_format_col2_row_-1.csv|
||column_heterogeneous_format_col2_row_2.csv|
||column_heterogeneous_format_col2_row_50.csv|
||column_heterogeneous_format_col2_row_range(1, 50).csv|
||column_heterogeneous_format_col2_row_range(30, 80).csv|
||column_heterogeneous_format_col2_row_range(50, 100).csv|
||column_heterogeneous_format_col3_row_-1.csv|
||column_heterogeneous_format_col3_row_2.csv|
||column_heterogeneous_format_col3_row_50.csv|
||column_heterogeneous_format_col3_row_range(1, 50).csv|
||column_heterogeneous_format_col3_row_range(30, 80).csv|
||column_heterogeneous_format_col3_row_range(50, 100).csv|
||column_heterogeneous_format_col4_row_-1.csv|
||column_heterogeneous_format_col4_row_2.csv|
||column_heterogeneous_format_col4_row_50.csv|
||column_heterogeneous_format_col4_row_range(1, 50).csv|
||column_heterogeneous_format_col4_row_range(30, 80).csv|
||column_heterogeneous_format_col4_row_range(50, 100).csv|
||column_heterogeneous_format_col5_row_-1.csv|
||column_heterogeneous_format_col5_row_2.csv|
||column_heterogeneous_format_col5_row_50.csv|
||column_heterogeneous_format_col5_row_range(1, 50).csv|
||column_heterogeneous_format_col5_row_range(30, 80).csv|
||column_heterogeneous_format_col5_row_range(50, 100).csv|
||column_heterogeneous_format_col8_row_-1.csv|
||column_heterogeneous_format_col8_row_2.csv|
||column_heterogeneous_format_col8_row_50.csv|
||column_heterogeneous_format_col8_row_range(1, 50).csv|
||column_heterogeneous_format_col8_row_range(30, 80).csv|
||column_heterogeneous_format_col8_row_range(50, 100).csv|

</details>

Due to the GitHub file policy, the files composing the benchmark are contained in a compressed file (files/polluted.tar.gz).
The same files can be programmatically generated from the source file (files/source.csv), by running the command:

`python3 pollute_main.py`

The script produces the set of benchmark files in the two folders "files/polluted_files_csv/" and "files/polluted_files_xml/".
The former contains the generated polluted files in the .csv format, while the latter their XML trees with metadata attributes.

## Running the benchmark

To benchmark a specific system, load all the files in the "files/polluted_files_csv" folder and export them back in csv format in a new folder.
Then, use the benchmark.py script with the following command:

`python3 benchmark.py --sut sut_folder`

The script reports the overall success, completeness, and conciseness score and outputs the specific results for each of the benchmark files in a CSV file, whose path can be specified with the --result parameter.
For the full list of parameters, run:

`python3 benchmark.py --help`

## Experimental results

In the repository we include the result files of the benchmark on four different systems:
 - A spreadsheet system, named 'ss'
 - A data science programming framework, named 'ds'
 - A relational dbms, named 'db'
 - A data visualization and business intelligend tool, named 'bi'

For each of these systems, the resulting files from loading polluted files of our benchmark can be found in the file 'sut/systems.tar.gz'.
Extracting these files, users can reproduce the experimental results reported in our benchmark paper.
