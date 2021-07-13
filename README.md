# Pollock
Pollock is a benchmark for data loading on character-delimited files, developed at the Information Systems Group of the Hasso Plattner Institute.

## Setup

The code is written using Python 3.8.5.
If using a local (or virtual) environment, install dependencies with
`pip install -r requirements.txt`
Alternatively, if using a conda distribution on Linux, use:
`conda env create --file pollock.yml`

## Benchmark files
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