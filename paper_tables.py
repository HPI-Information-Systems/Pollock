import pandas as pd
import numpy as np
import math
import re

custom_order = {"clevercs": 0, "csvcommons": 1, "rhypoparsr": 2, "opencsv": 3, "pandas": 4, "pycsv": 5, "rcsv": 6, "univocity": 7, "mariadb": 8,
                    "mysql": 9, "postgres": 10, "sqlite": 11, "libreoffice": 12, "spreaddesktop": 13, "spreadweb": 14, "dataviz": 15}

SUTS = custom_order.keys()

def round_down(n, decimals=2):
    multiplier = 10 ** decimals
    return math.floor(n * multiplier) / float(multiplier)

# Get the loading times
def get_loading_times(sut, dataset, dataframe=None):

    # Check if dataframe is None, if not, read csv file
    sut_time_df = dataframe if dataframe is not None else pd.read_csv(f"results/{sut}/{dataset}/{sut}_time.csv")

    all_times = sut_time_df[sut_time_df.columns[1:]].values.flatten()

    # Calculate the benchmark_time by calculating the mean (average) of the loading times
    benchmark_time = all_times.mean()

    # Calculate the square root of the variance of the loading times
    benchmark_time_std = np.sqrt(np.var(all_times))

    return f'{round(benchmark_time * 1000, 2)} +- {round(benchmark_time_std * 1000, 2)}'

def generate_table_5():
     # Read the csv file
    df = pd.read_csv('results/global_results_polluted_files.csv')

    headers = ['S', 'HF1', 'RF1', 'CF1', 'Loading time (ms)']

    # Create a table that has the sut as index and the headers as columns. Sut gotten from the custom order
    table = pd.DataFrame(columns=headers, index=custom_order.keys())

    # Get from df the row where file is "source.csv"
    source_row = df.loc[df['file'] == 'source.csv']


    # Fill the table
    for sut in custom_order.keys():

        # Only add the ones where success, header_f1, record_f1 and cell_f1 are not 1
        if source_row[f'{sut}_success'].values[0] == 1 and source_row[f'{sut}_header_f1'].values[0] == 1 and source_row[f'{sut}_record_f1'].values[0] == 1 and source_row[f'{sut}_cell_f1'].values[0] == 1:
            # Remove the sut from the table
            table = table.drop(sut)
            continue

        table.loc[sut, 'S'] = round_down(source_row[f'{sut}_success'].values[0])
        table.loc[sut, 'HF1'] = round_down(source_row[f'{sut}_header_f1'].values[0])
        table.loc[sut, 'RF1'] = round_down(source_row[f'{sut}_record_f1'].values[0])
        table.loc[sut, 'CF1'] = round_down(source_row[f'{sut}_cell_f1'].values[0])

        # Create a dataframe with just the row where file is "source.csv"
        source_row_time_df = pd.read_csv(f"results/{sut}/polluted_files/{sut}_time.csv")
        source_row_time_df = source_row_time_df.loc[source_row_time_df['filename'] == 'source.csv']

        # Get the loading times
        table.loc[sut, 'Loading time (ms)'] = get_loading_times(sut=sut, dataset='polluted_files', dataframe=source_row_time_df)

    
    return table

def generate_table_6():
    df = pd.read_csv('results/global_results_polluted_files.csv')
    df.set_index('file', inplace=True)

    headers = ['File and table pollution', 
               'Inconsistent number of delimiters', 
               'Structural character change']
    subheaders = ['S', 'HF1', 'RF1', 'CF1']
    rexes = ["file_double.*|file_header.*|file_no.*|file_one.*|file_multi.*|file_preamble.*",
            "%row_less.*|row_more",
            "file_field.*|row_field.*|file_quote.*|file_record_delimiter.*|row_extra_quote.*|file_escape.*"]
    
    metrics = ['success', 'header_f1', 'record_f1', 'cell_f1']

    # Create the table index (with the headers and subheaders), append the pollock score and loading time
    table_header = pd.MultiIndex.from_product([headers, subheaders])
    table_header = table_header.insert(len(table_header), ('Pollock score', 'Simple'))
    table_header = table_header.insert(len(table_header), ('Pollock score', 'Weighted'))
    table_header = table_header.insert(len(table_header), ('Loading time (ms)', ''))

    table = pd.DataFrame(columns=table_header, index=SUTS)

    for sut in SUTS:
        for idx,header in enumerate(headers):
            rx = rexes[idx]
            files = [f for f in df.index if re.search(rx,f)]

            means = df.loc[files].mean()
            for jdx, metric in enumerate(metrics):
                value = means[sut + "_" + metric]
                table.loc[sut, (header, subheaders[jdx])] = round_down(value)

        pollock_simple = sum(df.mean().loc[[c for c in df.columns if sut in c]])
        table.loc[sut, ("Pollock score", "Simple")] = round_down(pollock_simple)

        partial_mean = df[[c for c in df.columns if sut in c]].sum(axis=1) * df["normalized_weight"]
        pollock_weighted = sum(partial_mean)
        table.loc[sut, ("Pollock score", "Weighted")] = round_down(pollock_weighted)

        loading_time = get_loading_times(sut=sut, dataset='polluted_files')
        table.loc[sut, ("Loading time (ms)", "")] = loading_time

    return table


def generate_table_7():

    df = pd.read_csv('results/global_results_survey_sample.csv')
    df.set_index('file', inplace=True)

    headers = ['S', 'HF1', 'RF1', 'CF1', 'Po.', 'Loading time (ms)']
    metrics = ['success', 'header_f1', 'record_f1', 'cell_f1', 'pollock_simple', 'loading_time']

    table = pd.DataFrame(columns=headers, index=SUTS)

    for sut in SUTS:
        for idx,header in enumerate(headers):
            metric = metrics[idx]
            if metric == 'loading_time':
                value = get_loading_times(sut=sut, dataset='survey_sample') 
            elif metric == 'pollock_simple':
                pollock_simple = sum(df.mean().loc[[c for c in df.columns if sut in c]])
                value = round_down(pollock_simple)
            else:
                means = df.mean()
                value = means[sut + "_" + metric]
                value = round_down(value)

            table.loc[sut, header] = value

    return table


if __name__ == "__main__":
    table_5 = generate_table_5()
    print('---------- Table 5: Systems with imperfect loading of the source file (RFC4180 compliant): success and F1-scores. ----------')
    print()
    print(table_5)
    print()

    table_6 = generate_table_6()
    print('---------- Table 6: Pollock results (rounding down) of the 16 systems under test, grouped by pollution type. ----------')
    print('\n\tFile and table pollution (12 files)')
    print(table_6['File and table pollution'])

    print('\n\tInconsistent number of delimiters (1428 files)')
    print(table_6['Inconsistent number of delimiters'])
    
    print('\n\tStructural character change (850 files)')
    print(table_6['Structural character change'])
    
    print('\n\tPollock score (2289 +1 files) and Average file-wise time (ms)')
    print(table_6[['Pollock score', 'Loading time (ms)']])
    print()
    # Uncomment for full table
    # print(table_6)


    table_7 = generate_table_7()
    print('---------- Table 7: Results on a sample of 100 files from our survey. ----------')
    print()
    print(table_7)
    print()





