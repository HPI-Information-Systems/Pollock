"""
This script evaluates the results of polluted data loading from a system.
The input is a set of files resulting from a systems' loading in the {sut} folder, and their original benchmark XML in /files/polluted_files_xml
Launch with --help to see the complete list of command line parameters.
"""


from __future__ import print_function
import builtins as __builtin__
from datetime import datetime
import argparse
import time
import os
import pandas as pd
from lxml import etree
from pathlib import Path
import metrics


from CSVFile import CSVFile

TO_SKIP = [] #debug purpose

def print(*args, **kwargs):
    return __builtin__.print(f"\033[94m{datetime.fromtimestamp(time.time()+3600).strftime('%H:%M:%S')}:\033[0m", *args, **kwargs)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sut", default="files/ss/", help="The folder containing the results of the sut to benchmark")
    parser.add_argument("--polluted", default="files/polluted_files_xml/", help="The folder containg the XML polluted benchmark files")
    parser.add_argument("--result", default = "result.csv", help= "The path where the result csv file will be saved")
    parser.add_argument("--verbose", default=False, help="Whether to print filenames as they are processed")

    args = parser.parse_args()
    SUT_DIR = args.sut
    POLLUTED_DIR = args.polluted
    RESULT_FILE = args.result
    verbose = bool(args.verbose)

    print("Evaluating files in", SUT_DIR, "...")
    files = []
    success = []
    complete = []
    concise = []
    for polluted_file in os.listdir(POLLUTED_DIR):
        if polluted_file[-3:] != "xml" or polluted_file[:-4] in TO_SKIP:
            continue

        filename = polluted_file[:-4] #exclude ".xml"

        if verbose: print(f"'{filename}'")
        try:
            f1_tree = etree.parse(os.path.join(POLLUTED_DIR,polluted_file))
            f2_path = os.path.join(SUT_DIR,filename + "_converted.csv")
            f2 = CSVFile(f2_path, autodetect=False)
            succ = metrics.successful(f2.xml)
            comp = metrics.completeness(f1_tree, f2.xml) if succ else 0
            conc = metrics.conciseness(f1_tree,f2.xml) if succ else 0

        except Exception as e:
            print("Exception:",e)
            if not verbose: print("On file:", filename)
            succ = comp = conc = 0

        success += [succ]
        complete +=[comp]
        concise +=[conc]
        files += [filename]

    results_df = pd.DataFrame({"file":files, "success":success, "complete":complete, "concise":concise})
    results_df.to_csv(RESULT_FILE, index=False)
    if verbose: print(results_df)
    s, cp, cn = results_df[["success","complete","concise"]].sum()
    print("Success:", s)
    print("Completeness:", cp)
    print("Conciseness:", cn)
    print("Overall score:", s+cp+cn)
    return

if __name__ == "__main__":
    main()
