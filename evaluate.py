from __future__ import print_function
import os
from pqdm.processes import pqdm
import pandas as pd
from lxml import etree
import pollock.metrics as metrics
from sut.utils import print
from pollock.CSVFile import CSVFile
import argparse

def evaluate_single_file(polluted_dir, result_dir="", filename="", sut="", verbose=False):
    if type(polluted_dir) == list: #Required for multiprocessing
        polluted_dir, result_dir, filename, sut, verbose = polluted_dir[0], polluted_dir[1], polluted_dir[2], polluted_dir[3], polluted_dir[4]
    sut_dir = f"{result_dir}/loading/{sut}/"

    dict_measures = {"file": filename}

    if verbose:
        print(f"'{filename}'")
    try:
        f1_tree = etree.parse(polluted_dir + filename + ".xml")
        f2 = CSVFile(sut_dir + filename + "_converted.csv", autodetect=False)
        succ = metrics.successful(f2.xml)
        dict_measures[sut + "_success"] = succ
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
        if not verbose:
            print("On file:", filename)
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


def evaluate_single_run(polluted_dir, result_dir, sut, verbose=False, njobs=-1):
    filenames = [pf[:-4] for pf in os.listdir(polluted_dir) if (pf.endswith("xml"))]

    if os.cpu_count() < njobs or njobs == -1:
        file_measures = list(map(lambda f: evaluate_single_file(polluted_dir, result_dir, f, sut, verbose=verbose), filenames))
    else:
        args = [list(x) for x in zip([polluted_dir] * len(filenames),
                                     [result_dir] * len(filenames),
                                     filenames,
                                     [sut] * len(filenames),
                                     [verbose] * len(filenames))]
        file_measures = pqdm(args, evaluate_single_file, n_jobs=njobs)
    results_df = pd.DataFrame(file_measures)
    result_file = f"{result_dir}/measures/{sut}_results.csv"
    results_df.to_csv(result_file, index=False)

    if verbose:
        print(results_df)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sut", default=None, help="The single system to benchmark, if not running the evaluation for all of them")
    parser.add_argument("--polluted", default="./results/polluted_files_xml/", help="The folder containg the XML polluted benchmark files")
    parser.add_argument("--result", default="./results", help="The root path where the results of the loading are")
    parser.add_argument("--verbose", default=False, help="Whether to print filenames as they are processed")
    parser.add_argument("--njobs", default=100, help="The number of jobs to parallelize the computation")

    args = parser.parse_args()
    UPDATE_SYSTEM = args.sut
    POLLUTED_DIR = args.polluted
    RESULT_DIR = args.result
    N_JOBS = int(args.njobs)

    verbose = bool(args.verbose)

    systems = [s for s in next(os.walk(f"{RESULT_DIR}/loading"))[1] if not ((s == "archives") or ("old" in s))]
    files = [f[:-4] for f in os.listdir(POLLUTED_DIR) if f[-3:] == "xml"]
    aggregate = []
    global_df = pd.DataFrame({"file": files})
    for s in systems:
        if UPDATE_SYSTEM is not None and s != UPDATE_SYSTEM:
            pass
        else:
            print("Evaluating", s, "...")
            evaluate_single_run(POLLUTED_DIR, RESULT_DIR, s, njobs=N_JOBS, verbose=verbose)
        df = pd.read_csv(f"{RESULT_DIR}/measures/{s}_results.csv")
        d_aggregate = {"".join(key.split("_")[1:]): val for key, val in df.mean(axis=0, numeric_only=True).items()}
        d_aggregate.update({"sut": s})
        aggregate += [d_aggregate]
        global_df = global_df.merge(df, how="outer", left_on="file", right_on="file")  # , suffixes=(None,"_"+s))
    aggregate_df = pd.DataFrame(aggregate).set_index("sut")
    aggregate_df["overall"] = aggregate_df.sum(axis=1, numeric_only=True)
    global_df.to_csv(RESULT_DIR + "/global_results.csv", index=False)
    aggregate_df.to_csv(RESULT_DIR + "/aggregate_results.csv")


if __name__ == "__main__":
    main()
