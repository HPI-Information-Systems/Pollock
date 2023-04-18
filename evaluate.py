from __future__ import print_function
import json
import os
import argparse
import traceback

from pqdm.processes import pqdm
import pandas as pd
from typing import List

import pollock.metrics as metrics
from sut.utils import print

from dotenv import load_dotenv
load_dotenv()

def evaluate_single_file(filename:str, dataset:str, sut:str, verbose=False, n_jobs=1):
    sut_dir = f"results/{sut}/{dataset}/loading/"
    clean_path = f"{dataset}/clean/{filename}"
    loaded_path = f"{sut_dir}/{filename}_converted.csv"

    dict_measures = {"file": filename}
    if verbose:
        print(f"'{filename}'")
    try:
        succ = metrics.successful_csv(loaded_path)
        dict_measures[sut + "_success"] = succ
        dict_measures[sut + "_header_precision"], \
        dict_measures[sut + "_header_recall"], \
        dict_measures[sut + "_header_f1"], \
        dict_measures[sut + "_record_precision"], \
        dict_measures[sut + "_record_recall"], \
        dict_measures[sut + "_record_f1"], \
        dict_measures[sut + "_cell_precision"], \
        dict_measures[sut + "_cell_recall"], \
        dict_measures[sut + "_cell_f1"] = metrics.header_record_cell_measures_csv(clean_path,loaded_path, n_jobs) \
            if succ else [0, 0, 0, 0, 0, 0, 0, 0, 0]

    except Exception as e:
        print("Exception:", traceback.format_exc())
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


def evaluate_single_run(files: List[str], dataset: str, result_file:str, sut:str, verbose=False, n_jobs=1):

    if os.cpu_count()< n_jobs:
        file_measures = list(map(lambda f: evaluate_single_file(filename=f, dataset=dataset, sut=sut, verbose=verbose), files))
    else:
        tiny_files = [f for f in files if os.path.getsize(dataset+"/"+f)/ 1024 < 500]
        args = [{"filename" : f, "dataset":dataset, "sut": sut, "verbose": verbose} for f in tiny_files]
        tiny_file_measures = pqdm(args, evaluate_single_file, n_jobs=n_jobs, argument_type="kwargs")

        print("Evaluating large files...")
        large_filenames = [f for f in files if os.path.getsize(dataset+"/"+f)/ 1024 >= 500]
        large_file_measures = []
        for f in large_filenames:
            large_file_measures.append(evaluate_single_file(f, dataset, sut, verbose=verbose, n_jobs=n_jobs))

        file_measures = tiny_file_measures+large_file_measures
    results_df = pd.DataFrame(file_measures)
    results_df.to_csv(result_file, index=False)
    if verbose: print(results_df)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sut", default=None, help="The single system to benchmark, if not running the evaluation for all of them")
    parser.add_argument("--dataset", default="polluted_files", help="The dataset containing the input CSV files")
    parser.add_argument("--result", default="./results", help="The root path where the results of the loading are")
    parser.add_argument("--verbose", default=False, help="Whether to print filenames as they are processed")
    parser.add_argument("--njobs", default=100, help="The number of jobs to parallelize the computation")

    args = parser.parse_args()
    UPDATE_SYSTEM = args.sut
    dataset = args.dataset
    RESULT_DIR = args.result
    N_JOBS = int(args.njobs)

    verbose = bool(args.verbose)
    systems = [s for s in next(os.walk(f"{RESULT_DIR}"))[1] if not (s== "archives")]

    files= [f for f in os.listdir(dataset+"/csv") if f.endswith("csv")]
    aggregate = []
    global_df = pd.DataFrame({"file": files})
    for s in systems:
        result_file = f"{RESULT_DIR}/{s}/{dataset}/{s}_results.csv"
        if UPDATE_SYSTEM is not None and s != UPDATE_SYSTEM:
            pass
        else:
            print("\nEvaluating", s, "...")
            evaluate_single_run(files=files, dataset=dataset, result_file=result_file, sut=s, n_jobs=N_JOBS, verbose=verbose)
        df = pd.read_csv(f"{RESULT_DIR}/measures/{s}_results.csv")
        d_aggregate = {"".join(key.split("_")[1:]): val for key, val in df.mean(axis=0, numeric_only=True).items()}
        d_aggregate.update({"sut": s})
        aggregate += [d_aggregate]
        global_df = global_df.merge(df, how="outer", left_on="file", right_on="file")  # , suffixes=(None,"_"+s))
    aggregate_df = pd.DataFrame(aggregate).set_index("sut")
    aggregate_df["simple"] = aggregate_df.sum(axis=1, numeric_only=True)

    if dataset == "polluted_files":
        with open("pollock_weights.json", "r") as f:
            weights = json.load(f)
        global_df["weight"] = [weights.get(x, -1) for x in global_df["file"].tolist()]
        global_df["normalized_weight"] = global_df["weight"] / sum(global_df["weight"])
        for sut in systems:
            partial_mean = global_df[[c for c in global_df.columns if sut in c]].sum(axis=1) * global_df["normalized_weight"]
            weighted_score = sum(partial_mean)
            aggregate_df.loc[sut, "weighted"] = weighted_score
        print("\n",aggregate_df[["simple","weighted"]])

    else:
        print("\n", aggregate_df[["simple"]])

    global_df.to_csv(RESULT_DIR + f"/global_results_{dataset}.csv", index=False)
    aggregate_df.to_csv(RESULT_DIR + f"/aggregate_results_{dataset}.csv")

if __name__ == "__main__":
    main()
