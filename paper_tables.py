import pandas as pd
import numpy as np
import math

custom_order = {"clevercs": 0, "csvcommons": 1, "rhypoparsr": 2, "opencsv": 3, "pandas": 4, "pycsv": 5, "rcsv": 6, "univocity": 7, "mariadb": 8,
                    "mysql": 9, "postgres": 10, "sqlite": 11, "libreoffice": 12, "spreaddesktop": 13, "spreadweb": 14, "dataviz": 15}

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

    headers = ['𝑆', '𝐻𝐹1', '𝑅𝐹1', '𝐶𝐹1', 'Loading time (ms)']

    # Create a table that has the sut as index and the headers as columns. Sut gotten from the custom order
    table_5 = pd.DataFrame(columns=headers, index=custom_order.keys())

    # Get from df the row where file is "source.csv"
    source_row = df.loc[df['file'] == 'source.csv']


    # Fill the table
    for sut in custom_order.keys():

        # Only add the ones where success, header_f1, record_f1 and cell_f1 are not 1
        if source_row[f'{sut}_success'].values[0] == 1 and source_row[f'{sut}_header_f1'].values[0] == 1 and source_row[f'{sut}_record_f1'].values[0] == 1 and source_row[f'{sut}_cell_f1'].values[0] == 1:
            # Remove the sut from the table
            table_5 = table_5.drop(sut)
            continue

        table_5.loc[sut, '𝑆'] = round_down(source_row[f'{sut}_success'].values[0])
        table_5.loc[sut, '𝐻𝐹1'] = round_down(source_row[f'{sut}_header_f1'].values[0])
        table_5.loc[sut, '𝑅𝐹1'] = round_down(source_row[f'{sut}_record_f1'].values[0])
        table_5.loc[sut, '𝐶𝐹1'] = round_down(source_row[f'{sut}_cell_f1'].values[0])

        # Create a dataframe with just the row where file is "source.csv"
        source_row_time_df = pd.read_csv(f"results/{sut}/polluted_files/{sut}_time.csv")
        source_row_time_df = source_row_time_df.loc[source_row_time_df['filename'] == 'source.csv']

        # Get the loading times
        table_5.loc[sut, 'Loading time (ms)'] = get_loading_times(sut=sut, dataset='polluted_files', dataframe=source_row_time_df)

    
    return table_5

def generate_table_6():
    # Read the csv file
    df = pd.read_csv('results/aggregate_results_polluted_files.csv')

    # Headers and subheaders
    headers = ['File and table pollution', 'Inconsistent number of delimiters', 'Structural character change']
    subheaders = ['𝑆', '𝐻𝐹1', '𝑅𝐹1', '𝐶𝐹1']


    # Create the table (with the headers and subheaders), but Pollock score should contain Simple and Weighted as subheaders, not the other ones
    table_header = pd.MultiIndex.from_product([headers, subheaders])

    # Edit the table to add the Pollock score subheaders
    table_header = table_header.insert(12, ('Pollock score', 'Simple'))
    table_header = table_header.insert(13, ('Pollock score', 'Weighted'))
    table_header = table_header.insert(14, ('Loading time (ms)', ''))

    table = pd.DataFrame(columns=table_header, index=df['sut'])

    # Fill the table
    for _, row in df.iterrows():
        # File and table pollution
        table.loc[row['sut'], ('File and table pollution', '𝑆')] = round_down(row['success'])
        table.loc[row['sut'], ('File and table pollution', '𝐻𝐹1')] = round_down(row['headerf1'])
        table.loc[row['sut'], ('File and table pollution', '𝑅𝐹1')] = round_down(row['recordf1'])
        table.loc[row['sut'], ('File and table pollution', '𝐶𝐹1')] = round_down(row['cellf1'])

        # Inconsistent number of delimiters
        table.loc[row['sut'], ('Inconsistent number of delimiters', '𝑆')] = round_down(row['inconsistent_success'])
        table.loc[row['sut'], ('Inconsistent number of delimiters', '𝐻𝐹1')] = round_down(row['inconsistent_header_f1'])
        table.loc[row['sut'], ('Inconsistent number of delimiters', '𝑅𝐹1')] = round_down(row['inconsistent_record_f1'])
        table.loc[row['sut'], ('Inconsistent number of delimiters', '𝐶𝐹1')] = round_down(row['inconsistent_cell_f1'])

        # Structural character change
        table.loc[row['sut'], ('Structural character change', '𝑆')] = round_down(row['structural_success'])
        table.loc[row['sut'], ('Structural character change', '𝐻𝐹1')] = round_down(row['structural_header_f1'])
        table.loc[row['sut'], ('Structural character change', '𝑅𝐹1')] = round_down(row['structural_record_f1'])
        table.loc[row['sut'], ('Structural character change', '𝐶𝐹1')] = round_down(row['structural_cell_f1'])

        # Pollock score
        table.loc[row['sut'], ('Pollock score', 'Simple')] = round_down(row['pollock_simple'])
        table.loc[row['sut'], ('Pollock score', 'Weighted')] = round_down(row['pollock_weighted'])

        # Get the loading times
        table.loc[row['sut'], ('Loading time (ms)', '')] = get_loading_times(sut=row['sut'], dataset='polluted_files')

    # Sort the table by the custom order
    table = table.sort_values(by=['sut'], key=lambda x: x.map(custom_order))

    return table


def generate_table_7():
    # Read the csv file
    df = pd.read_csv('results/aggregate_results_survey_sample.csv')

    headers = ['𝑆', '𝐻𝐹1', '𝑅𝐹1', '𝐶𝐹1', 'Po.', 'Loading time (ms)']

    # Create a table that has the sut as index and the headers as columns
    table_7 = pd.DataFrame(columns=headers, index=df['sut'])

    # Fill the table
    for _, row in df.iterrows():
        table_7.loc[row['sut'], '𝑆'] = round_down(row['success'])
        table_7.loc[row['sut'], '𝐻𝐹1'] = round_down(row['headerf1'])
        table_7.loc[row['sut'], '𝑅𝐹1'] = round_down(row['recordf1'])
        table_7.loc[row['sut'], '𝐶𝐹1'] = round_down(row['cellf1'])
        table_7.loc[row['sut'], 'Po.'] = round_down(row['pollock_simple'])

        # Get the loading times
        table_7.loc[row['sut'], 'Loading time (ms)'] = get_loading_times(sut=row['sut'], dataset='survey_sample')
    
    return table_7

if __name__ == "__main__":
    table_5 = generate_table_5()
    print('---------- Table 5: Systems with imperfect loading of the source file (RFC4180 compliant): success and F1-scores. ----------')
    print()
    print(table_5)
    print()

    table_6 = generate_table_6()
    print('---------- Table 6: Pollock results (rounding down) of the 16 systems under test, grouped by pollution type. ----------')
    print()
    print(table_6)
    print()

    table_7 = generate_table_7()
    print('---------- Table 7: Results on a sample of 100 files from our survey. ----------')
    print()
    print(table_7)
    print()





