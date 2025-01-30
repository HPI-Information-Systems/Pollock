# Pollock
Pollock is a benchmark for data loading on character-delimited files, developed at the Information Systems Group of the Hasso Plattner Institute.
The highlights of our experiments are these results, obtained on 17 different systems under test:
<div align="center">

## Pollock Score (Simple)

| System under test        | Pollock score (simple)  |
| ------------------------ | ----------------------- |
| DuckDB 1.2               | **9.961**               |
| SQLite 3.39.0            | **9.955**               |
| UniVocity 2.9.1          | **9.939**               |
| LibreOffice Calc 7.3.6   | **9.925**               |
| SpreadDesktop            | **9.929**               |
| SpreadWeb                | **9.721**               |
| Python native csv 3.10.5 | **9.721**               |
| Pandas 1.4.3             | **9.895**               |
| MySQL 8.0.31             | **9.587**               |
| Mariadb 10.9.3           | **9.585**               |
| CleverCSV 0.7.4          | **9.193**               |
| DuckDB 1.2 (Auto)        | **9.075**               |
| R native csv 4.2.1       | **7.792**               |
| CSVCommons 1.9.0         | **6.647**               |
| OpenCSV 5.6              | **6.632**               |
| Dataviz                  | **5.003**               |
| Hypoparsr 0.1.0          | **3.888**               |
| PostgreSQL 15.0          | **0.136**               |

## Pollock Score (Weighted)

| System under test        | Pollock score (weighted)  |
| ------------------------ | ------------------------- |
| DuckDB 1.2               | **9.599**                 |
| SpreadDesktop            | **9.597**                 |
| CleverCSV 0.7.4          | **9.453**                 |
| Python native csv 3.10.5 | **9.436**                 |
| SpreadWeb                | **9.431**                 |
| Pandas 1.4.3             | **9.431**                 |
| SQLite 3.39.0            | **9.375**                 |
| CSVCommons 1.9.0         | **9.253**                 |
| DuckDB 1.2 (Auto)        | **8.439**                 |
| UniVocity 2.9.1          | **7.936**                 |
| LibreOffice Calc 7.3.6   | **7.833**                 |
| OpenCSV 5.6              | **7.746**                 |
| MySQL 8.0.31             | **7.484**                 |
| Mariadb 10.9.3           | **7.483**                 |
| PostgreSQL 15.0          | **6.961**                 |
| R native csv 4.2.1       | **6.405**                 |
| Dataviz                  | **5.152**                 |
| Hypoparsr 0.1.0          | **4.372**                 |



</div>

## Repository structure

The structure of the repository is the following:

- `open_data_crawl`: contains the scripts used to crawl the open data portals of different countries to sample the statistics about file types.
- `survey`: contains the csv files used in the paper survey, and their annotations with respect to dialect and pollutions.
- `survey_sample`: contains the sample of 100 files used in the paper experiment, with their clean versions and loading parameters.
- `polluted_files`: contains the generated polluted files for the Pollock benchmark.
- `pollock` is the main source folder for the Pollock benchmark: it contains the files necessary to generate the polluted versions of an input file (`polluters_base.py` and `polluters_stdlib.py`) as well as the files with the metrics to evaluate results of data loading.
- `sut` is the source folder that contains the scripts used to benchmark given systems. These scripts can be in bash, python, or heterogeneous format, depending on the specific tool that is under test.
- `results` contains the results of loading both the polluted files and the survey files for each of the systems evaluated. The folder will also contain `.csv` files that summarize the evaluation results - for each of the systems under test and for all of them together (`aggregate_results_{dataset}.csv`, `global_results_{dataset}.csv`).
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

After this step, the set of benchmark files are contained in the folder `polluted_files`.
Inside this folder there are three sub-folders: `csv` containing the generated polluted files in the .csv format, 
`clean` containing the cleaned versions of the generated files, and `parameters` containing JSON files storing the corresponding loading parameters for each file.
The files in the repository uses Git Large File Storage (LFS), so to correctly load their contents use:
```git lfs checkout```.

### Step 2: Loading polluted files in each SUT
Once the folder `polluted_files/` contains the polluted files, the next step is to load them in each of the systems under test. 
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
    docker-compose up duckdbparse-client
    docker-compose up duckdbauto-client
</details>

At the end of the loading stages, the results will be available in the folder `results/{sut}/polluted_files`, where `{sut}` stands for a given SUT name.
Alternatively, the results of this step can be found in the repository.
If users wish to skip step 2, they can extract each systems' archive in the folder `results/{sut}`.
We also include archives for the `spreadweb`, `spreaddesktop`, and `dataviz` systems, for which due to their commercial nature, we do not share the scripts to obtain the output files.

### Step 3: Pollock scores calculation
To run the evaluation step, use the command:

    docker-compose up evaluate

The script outputs the benchmark scores for each of the polluted files in a csv file under `results/{sut}/` for each of the systems.
Moreover, all results are saved in the file `results/global_results_polluted_files.csv` and aggregated in the file `results/aggregate_results_polluted_files.csv`.
The script also outputs the results of the benchmark with the simple and weighted Pollock scores.

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

`docker-compose run evaluate python3 evaluate.py --sut pycsv-client`

The script reports the overall success, completeness, and conciseness score and outputs the specific results for each of the benchmark files in a CSV file, whose path can be specified with the --result parameter.
(This command updates the result CSV files).

For the full list of parameters, run:

`docker-compose run evaluate python3 evaluate.py --help`

## Extra: Change experiment dataset
The repository contains a .env file that every scripts reads from, specifying which dataset to run the experiments on.
The default setting is the `polluted_file` dataset, to run experiments for the survey sample, simply comment out the first line and uncomment the second line of the file.
To experiment with the survey sample file, its content should be as follows:
```
    #DATASET=polluted_files
    DATASET=survey_sample
```
To evaluate the results of the survey sample, run evaluate script with:
```
    docker-compose run evaluation python3 evaluate.py --dataset survey_sample
```
