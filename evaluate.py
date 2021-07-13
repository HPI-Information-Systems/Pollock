from __future__ import print_function
import builtins as __builtin__
from datetime import datetime
import time
import os
import pandas as pd
from lxml import etree
from pathlib import Path
import metrics

from CSVFile import CSVFile

TO_SKIP = []

DEBUG = False

def print(*args, **kwargs):
    return __builtin__.print(f"\033[94m{datetime.fromtimestamp(time.time()+3600).strftime('%H:%M:%S')}:\033[0m", *args, **kwargs)

def evaluate_single_run(RESULT_DIR, sut, verbose=False):
    POLLUTED_DIR = f"{RESULT_DIR}/files/polluted_files_xml/"
    SUT_DIR = f"{RESULT_DIR}/files/{sut}/"
    RESULT_FILE = f"{RESULT_DIR}/{sut}_results.csv"

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
            f1_tree = etree.parse(POLLUTED_DIR+polluted_file)
            f2 = CSVFile(SUT_DIR + filename + "_converted.csv", autodetect=False)
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

    results_df = pd.DataFrame({"file":files, sut+"_loaded":success, sut+"_complete":complete, sut+"_concise":concise})
    if not DEBUG:
        results_df.to_csv(RESULT_FILE, index=False)
    else:
        print(results_df)

    if verbose: print(results_df)
    return files

def main():
    RESULT_DIR = "./"
    POLLUTED_DIR = f"{RESULT_DIR}/files/polluted_files_xml/"
    systems = ["ss","db", "ds","bi"]

    files = [f[:-4] for f in os.listdir(POLLUTED_DIR) if f[-3:]== "xml"]

    if DEBUG: print("THIS IS A DEBUG RUN, NOT SAVING ANYTHING")
    global_df = pd.DataFrame({"file": files})
    for s in systems:
        print("Evaluating", s, "...")
        evaluate_single_run(RESULT_DIR,s)
        df = pd.read_csv(f"{RESULT_DIR}/{s}_results.csv")
        global_df = global_df.merge(df, how="outer", left_on="file", right_on="file")

    if not DEBUG:
        global_df.to_csv(RESULT_DIR+"/global_results.csv", index=False)
    print(global_df.columns)

if __name__ == "__main__":
    main()
