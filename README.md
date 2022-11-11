# Pollock
Pollock is a benchmark for data loading on character-delimited files, developed at the Information Systems Group of the Hasso Plattner Institute.

## Repository structure

The structure of the repository is the following:

- `survey`: contains the csv files used in the paper survey, and their annotations with respect to dialect and pollutions.
- `pollock` is the main source folder for the Pollock benchmark: it contains the files necessary to generate the polluted versions of an input file (`polluters_base.py` and `polluters_stdlib.py`) as well as the files with the metrics to evaluate results of data loading.
- `sut` is the source folder that contains the scripts used to benchmark given systems. These scripts can be in bash, python, or heterogeneous format, depending on the specific tool that is under test.
- `results` contains the results of the pollution (`polluted_files_csv`, `polluted_files_xml`) as well as those of the loading by each of the systems (`loading`). The folder will also contain `.csv` files that summarize the evaluation results - for each of the systems under test and for all of them together (`aggregate_results.csv`, `global_results.csv`)
- The file `docker-compose.yml` contains a list of the docker images that are used to run the benchmark. The images are built from the `Dockerfile` files in the `sut` folder.
- The two files `pollute_main.py` and `evaluate.py` are used to run the pollution of a source file and to evaluate all systems under test that have a folder in `results/loading`


## Running the benchmark

The results of the Pollock benchmark can be obtained in three steps:

    1. Generating the polluted versions of the source files
    2. Loading the polluted files in each SUT.
    3. Calculating the Pollock scores with the output files for each SUT.

For convenience, in this repository we already provide the intermediate artifacts necessary to run the steps 2. and 3., so that our results can be reproduced with different degrees of completeness.
We include results for 16 different systems:
 - 6 csv loading modules: `clevercsv`,`csvcommons`,`hypoparsr`,`opencsv`,`pandas`,`pycsv`,`rcsv`, `univocity`
 - 4 rdbms: `mariadb`,`mysql`,`postgres`,`sqlite`
 - 3 spreadsheet systems: `libreoffice`,`spreaddesktop`,`spreadweb`
 - A data visualization tool, `dataviz`

### Step 1: Generating polluted files
The code for running the benchmark is written using Docker (and docker-compose).
The following command will build the docker image to generate the polluted files:

    docker-compose up --build pollution

After this step, the set of benchmark files are contained in the two folders "results/polluted_files_csv/" and "results/polluted_files_xml/".
The former contains the generated polluted files in the .csv format, while the latter their XML trees with metadata attributes.
The results of this steps can be found in the repository under `results/polluted_files_csv/` and `results/polluted_files_xml/`.
The files in the repository uses Git Large File Storage (LFS), so to correctly load their contents use:
```git lfs checkout```.

### Step 2: Loading polluted files in each SUT
Once the folder `results/polluted_files_csv/` contains the polluted files, the next step is to load them in each of the systems under test. 
If a unix-based systems is used, the following one-liner executes loading for all SUT:

    chmod +x benchmark.sh; ./benchmark.sh    

Otherwise, loading can be done by running the following docker-compose commands in a sequence:

<details>
<summary>Loading commands</summary>

    docker-compose up --detach mariadb-server mysql-server postgres-server
    docker-compose up opencsv-client
    docker-compose up csvcommons-client
    docker-compose up univocity-client
    docker-compose up pycsv-client
    docker-compose up pandas-client
    docker-compose up rcsv-client
    docker-compose up clevercs-client
    docker-compose up rhypoparsr-client
    docker-compose up libreoffice-client
    docker-compose up sqlite-client
    
    docker-compose up postgres-client
    docker-compose up mariadb-client
    docker-compose up mysql-client
</details>

At the end of the loading stages, the results will be available in the folder `results/loading/{sut}`, where `{sut}` stands for a given SUT name.
Alternatively, the results of this step can be found, for each of the SUT tested in the Pollock paper, archived in `results/loading/archives/`.
If users wish to skip step 2, by unzipping each systems' archive, the folder `results/loading/{sut}` will be created.
We also include archives for the `spreadweb`, `spreaddesktop`, and `dataviz` systems, for which due to their commercial nature, we do not share the scripts to obtain the output files.

### Step 3: Pollock scores calculation
To run the evaluation step, use the command:

    docker-compose up evaluation

The script outputs the benchmark scores for each of the polluted files in a csv file under `results/measures/` for each of the systems.
Moreover, all results are saved in the file `results/global_results.csv` and aggregated in the file `results/aggregate_results.csv`.

## Pollution list
For the complete list of benchmark files, expand the following table.
<details>
<summary>Pollock files</summary>

| Pollution level                                | File name                          | Pollution type                                                                                                                       |
|------------------------------------------------|------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------|
| Standard file                                  | source.csv                         | Standard file                                                                                                                        |
| File and table pollution (12 files)            | file_no_payload.csv                | Empty file, with a size of 0 bytes                                                                                                   |
|                                                | file_no_trailing_newline.csv       | File terminated without a newline sequence                                                                                           |
|                                                | file_double_trailing_newline.csv   | File terminated with a double newline sequence                                                                                       | 
|                                                | file_no_header.csv                 | File where there is no header row                                                                                                    |
|                                                | file_header_multirow_2.csv         | File where there are two header rows.                                                                                                |
|                                                | file_header_multirow_3.csv         | File where are three header rows.                                                                                                    |
|                                                | file_preamble.csv                  | File with a preamble rows delimited from the rest of the file with an empty row.                                                     |
|                                                | file_multitable_less.csv           | File with two tables, the first with less columns than the second.                                                                   |
|                                                | file_multitable_more.csv           | File with two tables, the first with more columns than the second.                                                                   |
|                                                | file_multitable_same.csv           | File with two tables with the same number of columns.                                                                                |
|                                                | file_header_only.csv               | File with only header row.                                                                                                           |
|                                                | file_one_data_row.csv              | File with a single data row.                                                                                                         |
| Inconsistent number of delimiters (1428 files) | row_less_sep_rowX_colY.csv         | File where row X has a missing delimiter corresponding to column Y (672 files, one for each row/col combination except first column) |
|                                                | row_more_sep_rowX_colY.csv         | File where row X has an extra delimiter corresponding to column Y (756 files, one for each row/col combination)                      |
| Structural character change (849 files)        | file_field_delimiter_0x20.csv      | File where fields are delimited with space.                                                                                          |
|                                                | file_field_delimiter_0x2C_0x20.csv | File where fields are delimited with comma and space.                                                                                |
|                                                | file_field_delimiter_0x3B.csv      | File where fields are delimited with semicolon.                                                                                      |
|                                                | file_field_delimiter_0x9.csv       | File where fields are delimited with tab.                                                                                            |
|                                                | file_quotation_char_0x27.csv       | File where the quotation character is the apostrophe.                                                                                |
|                                                | file_escape_char_0x5C.csv          | File where the escape character is the backslash.                                                                                    |
|                                                | file_escape_char_0x00.csv          | File where the escape character is missing.                                                                                          |
|                                                | file_record_delimiter_0xA.csv      | File where rows end with the LF character.                                                                                           |
|                                                | file_record_delimiter_0xD.csv      | File where rows end with the CR character.                                                                                           |
|                                                | row_extra_quoteX_colY.csv          | File where the cell in row X and column Y has an extra, unescaped quotation character (756 files, one for each row/col combination)  |
|                                                | row_field_delimiter_X_0x20.csv     | File where only row X is delimited with the space character (84 files one for each row)                                              |


</details>

## Extra: Benchmark a single SUT
To benchmark a specific system, you can use the Docker configurations in the file `docker-compose.yml`.
For example, to benchmark the python csv module:

`docker-compose up pycsv-client`

To benchmark the RDBMS systems, make sure to first run the corresponding server first, for example:

`docker-compose up postgres-server`
and, once the server is up and running:
`docker-compose up postgres-client`
To benchmark a specific system, run the `benchmark.py` script with the `--sut` argument followed by the name of the corresponding system folder, e.g.:

`docker-compose run evaluation python3 evaluate.py --sut pycsv-client`

The script reports the overall success, completeness, and conciseness score and outputs the specific results for each of the benchmark files in a CSV file, whose path can be specified with the --result parameter.
(This command updates the `global_results.csv` and `aggregate_results.csv` files).

For the full list of parameters, run:

`docker-compose run evaluation python3 evaluate.py --help`