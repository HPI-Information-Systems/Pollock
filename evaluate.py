from __future__ import print_function
import os
import pdb

from pqdm.processes import pqdm

import pandas as pd
from lxml import etree
import pollock.metrics as metrics
from sut.utils import print
from pollock.CSVFile import CSVFile

TO_SKIP = []

DEBUG = False
SUBSET = None
N_JOBS = 100

RESULT_DIR = "./results"
POLLUTED_DIR = f"{RESULT_DIR}/polluted_files_xml/"

#Set this as any system name to recompute the measures for that systems, set it to any non existing string to only merge the files,
#Set it to None to recompute everything
UPDATE_SYSTEM = None
# UPDATE_SYSTEM = "aggregate"
# UPDATE_SYSTEM = "mariadb"

def evaluate_single_file(filename, sut="", verbose=False):
    if type(filename) == list:
        filename, sut, verbose = filename[0], filename[1], filename[2]
    sut_dir = f"{RESULT_DIR}/loading/{sut}/"

    # exclude .xml
    dict_measures = {"file": filename}
    # files +=[filename]

    if verbose: print(f"'{filename}'")
    try:
        f1_tree = etree.parse(POLLUTED_DIR + filename + ".xml")
        f2 = CSVFile(sut_dir + filename + "_converted.csv", autodetect=False)
        succ = metrics.successful(f2.xml)
        dict_measures[sut + "_success"] = succ
        # comp = metrics.completeness_mwm(f1_tree,f2.xml) if succ else 0
        dict_measures[sut + "_header_precision"], \
        dict_measures[sut + "_header_recall"], \
        dict_measures[sut + "_header_f1"] = metrics.header_measures(f1_tree, f2.xml) if succ else [0, 0, 0]

        dict_measures[sut + "_record_precision"], \
        dict_measures[sut + "_record_recall"], \
        dict_measures[sut + "_record_f1"] = metrics.record_measures(f1_tree, f2.xml) if succ else [0, 0, 0]

        dict_measures[sut + "_cell_precision"], \
        dict_measures[sut + "_cell_recall"], \
        dict_measures[sut + "_cell_f1"] = metrics.cell_measures(f1_tree, f2.xml) if succ else [0, 0, 0]

    except Exception as e:
        print("Exception:", e)
        if not verbose: print("On file:", filename)
        for measure in ("header_precision",
                        "header_recall",
                        "header_f1",
                        "record_precision",
                        "record_recall",
                        "record_f1",
                        "cell_precision",
                        "cell_recall",
                        "cell_f1"):
            dict_measures[sut + "_" + measure] = 0

    return dict_measures

def evaluate_single_run(result_dir, sut, verbose=False):
    RESULT_FILE = f"{result_dir}/measures/{sut}_results.csv"

    filenames = [pf[:-4] for pf in os.listdir(POLLUTED_DIR)[:SUBSET] if (pf.endswith("xml") and pf not in TO_SKIP)]

    if os.cpu_count()< N_JOBS or DEBUG:
        if DEBUG: filenames = ["source.csv"]
        file_measures = list(map(lambda f: evaluate_single_file(f, sut, verbose=verbose), filenames ))
    else:
        args = [list(x) for x in zip(filenames, [sut]*len(filenames), [verbose]*len(filenames))]
        file_measures = pqdm(args, evaluate_single_file, n_jobs=N_JOBS)

    results_df = pd.DataFrame(file_measures)
    if not DEBUG:
        results_df.to_csv(RESULT_FILE, index=False)
    else:
        print(results_df)

    if verbose: print(results_df)

def main():
    POLLUTED_DIR = f"{RESULT_DIR}/polluted_files_xml/"
    systems = [s for s in next(os.walk(f"{RESULT_DIR}/loading"))[1] if not ((s== "archives") or ("old" in s))]
    files = [f[:-4] for f in os.listdir(POLLUTED_DIR)[:SUBSET] if f[-3:] == "xml"]
    if DEBUG: print("THIS IS A DEBUG RUN, NOT SAVING ANYTHING")
    aggregate = []
    global_df = pd.DataFrame({"file": files})
    for s in systems:
        print("Evaluating", s, "...")
        if UPDATE_SYSTEM is not None and s!= UPDATE_SYSTEM:
            pass
        else:
            evaluate_single_run(RESULT_DIR, s)
        df = pd.read_csv(f"{RESULT_DIR}/measures/{s}_results.csv")
        d_aggregate = {"".join(key.split("_")[1:]): val for key, val in df.mean(axis=0, numeric_only=True).items()}
        d_aggregate.update({"sut":s})
        aggregate +=[d_aggregate]
        global_df = global_df.merge(df, how="outer", left_on="file", right_on="file")  # , suffixes=(None,"_"+s))
        # if DEBUG: break
    aggregate_df = pd.DataFrame(aggregate).set_index("sut")
    aggregate_df["overall"] = aggregate_df.sum(axis=1, numeric_only=True)
    if not DEBUG:
        global_df.to_csv(RESULT_DIR + "/global_results.csv", index=False)
        aggregate_df.to_csv(RESULT_DIR + "/aggregate_results.csv")
    # print(global_df.columns)


if __name__ == "__main__":
    main()
