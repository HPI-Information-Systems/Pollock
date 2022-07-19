# Pollock
Pollock is a benchmark for data loading on character-delimited files, developed at the Information Systems Group of the Hasso Plattner Institute.

## Setup

The code is to generate pollutions and evaluate the results is written using Python 3.8.5.
If using a local (or virtual) Python environment, install dependencies with
`pip install -r requirements.txt`
Alternatively, if using a conda distribution on Linux, use:
`conda env create --file pollock.yml`

The code for running the benchmark is written using Docker (and docker-compose).
We recommend the use of a unix-based system to run our benchmark.
If docker-compose is installed in the system, all systems under test can be benchmarked with:

## Benchmark files
For the complete list of benchmark files, expand the following table.
<details>
<summary>Pollock files</summary>

| Pollution level                                | File name                                                                                                                           | Pollution type|
|------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------|-----------|
| Standard file                                  | source.csv                                                                                                                          | Standard file|
| File and table pollution (12 files)            | file_no_payload.csv                                                                                                                 |Empty file, with a size of 0 bytes|
|                                                | file_no_trailing_newline.csv                                                                                                        | File terminated without a newline sequence|
|                                                | file_double_trailing_newline.csv                                                                                                    | File terminated with a double newline sequence| 
|                                                | file_no_header.csv                                                                                                                  |File where there is no header row|
|                                                | file_header_multirow_2.csv                                                                                                          |File where there are two header rows.|
|                                                | file_header_multirow_3.csv                                                                                                          | File where are three header rows.|
|                                                | file_preamble.csv                                                                                                                   | File with a preamble rows delimited from the rest of the file with an empty row.|
|                                                | file_multitable_less.csv                                                                                                            |File with two tables, the first with less columns than the second.|
|                                                | file_multitable_more.csv                                                                                                            |File with two tables, the first with more columns than the second.|
|                                                | file_multitable_same.csv                                                                                                            |File with two tables with the same number of columns.|
|                                                | file_header_only.csv                                                                                                                |File with only header row.|
|                                                | file_one_data_row.csv                                                                                                               |File with a single data row.|
| Inconsistent number of delimiters (1428 files) | row_less_sep_rowX_colY.csv                                                                                                          |File where row X has a missing delimiter corresponding to column Y (672 files, one for each row/col combination except first column)|
|                                                | row_more_sep_rowX_colY.csv                                                                                                          |File where row X has an extra delimiter corresponding to column Y (756 files, one for each row/col combination)|
| Structural character change (847 files)        | file_field_delimiter_0x20.csv                                                                                                       |File where fields are delimited with space.|
|                                                | file_field_delimiter_0x2C_0x20.csv             | File where fields are delimited with comma and space.                                                                               |
|                                                | file_field_delimiter_0x3B.csv                  | File where fields are delimited with semicolon.                                                                                     |
|                                                | file_field_delimiter_0x9.csv                   | File where fields are delimited with tab.                                                                                           |
|                                                | file_quotation_char_0x27.csv                   | File where the quotation character is the apostrophe.                                                                               |
|                                                | file_record_delimiter_0xA.csv                  | File where rows end with the LF character.                                                                                          |
|                                                | file_record_delimiter_0xD.csv                  | File where rows end with the CR character.                                                                                          |
|                                                | row_extra_quoteX_colY.csv                      | File where the cell in row X and column Y has an extra, unescaped quotation character (756 files, one for each row/col combination) |
|                                                | row_field_delimiter_X_0x20.csv                 | File where only row X is delimited with the space character (84 files one for each row)                                             |


</details>

Due to the GitHub file policy, the files composing the benchmark are contained in a compressed file (files/polluted.tar.gz).
The same files can be programmatically generated from the source file (files/source.csv), by running the command:

`python3 pollute_main.py`

The script produces the set of benchmark files in the two folders "files/polluted_files_csv/" and "files/polluted_files_xml/".
The former contains the generated polluted files in the .csv format, while the latter their XML trees with metadata attributes.

## Running the benchmark

The structure of the project is the following:

- `pollock` is the main source folder for the Pollock benchmark: it contains the files necessary to generate the polluted versions of an input file (`polluters_base.py` and `polluters_stdlib.py`) as well as the files with the metrics to evaluate results of data loading.
- `sut` is the source folder that contains the scripts used to benchmark given systems. These scripts can be in bash, python, or heterogeneous format, depending on the specific tool that is under test.
- The two files `pollute_main.py` and `evaluate.py` are used to run the pollution of a source file and to evaluate all systems under test that have a folder in `results/loading`
- `results` contains the results of the pollution (`polluted_files_csv`, `polluted_files_xml`) as well as those of the loading by each of the systems (`loading`). The folder will also contain `.csv` files that summarize the evaluation results - for each of the systems under test and for all of them together (`aggregate_results.csv`, `global_results.csv`)
- `files` contains the sample csv files used to sample pollutions and generate the input file `source.csv`, along with their annotations.

### Create source file pollutions: 
First, to run the pollutions and recreate the content of `polluted_files_csv`, run:

`python3 pollute_main.py`

### Benchmarking SUT(s)
To run the overall benchmark on all systems, use the command:
`chmod +x benchmark.sh && benchmark.sh`

To benchmark a specific system, you can use the Docker configurations in the file `docker-compose.yml`.
For example, to benchmark the python csv module:

`docker-compose up pycsv-client`

To benchmark the RDBMS systems, make sure to first run the corresponding server first, for example:

`docker-compose up postgres-server`
and, once the server is up and running:
`docker-compose up postgres-client`

The script reports the overall success, completeness, and conciseness score and outputs the specific results for each of the benchmark files in a CSV file, whose path can be specified with the --result parameter.
For the full list of parameters, run:

`chmod +x benchmark.sh && ./benchmark.sh'`

### Experimental results
After running the benchmark for a given SUTs, the corresponding output files will be a corresponding folder in the `sut/loading/` directory.
Alternatively, the resulting files can be found in the repository under the `sut/archives/` folder as `.zip` files.
We also include archives for the `spreadweb`, `spreaddesktop`, and `dataviz` systems, for which due to their commercial nature, we do not share the scripts to obtain the output files.

To run the evaluation without running the benchmark, extract each `.zip` file in the `sut/loading/` folder, and then run the evaluation script:
`unzip sut/archives/pycsv.zip -qd sut/loading/ `
`python3 evaluate.py `

The script outputs the benchmark scores for each of the polluted files in a csv file under `results/measures/` for each of the systems.
Moreover, all results are saved in the file `results/global_results.csv` and aggregated in the file `results/aggregate_results.csv`.

To benchmark a specific system, run the `benchmark.py` script with the `--sut` argument followed by the name of the corresponding system folder, e.g.:

`python3 evaluate.py --sut mysql`

(This command updates the `global_results.csv` and `aggregate_results.csv` files).

For the full list of parameters, run:

`python3 benchmark.py --help`

In the repository we include the pollution output, and the result files of the benchmark on 16 different systems:
 - 6 csv loading modules: `clevercsv`,`csvcommons`,`hypoparsr`,`opencsv`,`pandas`,`pycsv`,`rcsv`, `univocity`
 - 4 rdbms: `mariadb`,`mysql`,`postgres`,`sqlite`
 - 3 spreadsheet systems: `libreoffice`,`spreaddesktop`,`spreadweb`
 - A data visualization tool, `dataviz`