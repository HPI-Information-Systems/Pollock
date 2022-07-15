from __future__ import print_function
import builtins as __builtin__
import itertools
import multiprocessing
import pdb
from datetime import datetime
import numpy as np
import time
from multiset import Multiset

from scipy.optimize import linear_sum_assignment
from multiprocessing.pool import Pool

from .data_types import normalize_cell


def print(*args, **kwargs):
    return __builtin__.print(f"\033[94m{datetime.fromtimestamp(time.time() + 3600).strftime('%H:%M:%S')}:\033[0m", *args, **kwargs)


def successful(file_xml):
    """ f1 is am XML trees
    """
    if len([v.text for v in file_xml.xpath("//value") if v.text == "Application Error"]):
        return 0
    else:
        return 1


def row_score(source_row, target_row):
    s = Multiset(source_row)
    t = Multiset(target_row)
    i = s.intersection(t)
    return np.sum([v for k, v in i.items()])

    # score=0
    # start_cell = 0
    # for source_cell in source_row:
    #     if start_cell == len(target_row):
    #         break
    #     for i in range(start_cell,len(target_row)):
    #         if (source_cell or "") == (target_row[i] or ""):
    #             start_cell = i+1
    #             score+=1
    #             break
    # return score


def completeness_mwm(source_xml, loaded_xml):
    source_rows = [r.xpath("./cell[@role='header' or @role='data']") for r in source_xml.xpath("//row")]
    source_rows = [[normalize_cell(cell) for cell in r] for r in source_rows if len(r)]

    if not len(source_rows):
        return 0

    loaded_rows = [r.xpath("./cell") for r in loaded_xml.xpath("//row")]
    loaded_rows = [[normalize_cell(cell) for cell in r] for r in loaded_rows]

    if not len(loaded_rows):
        return 0

    total_cores = multiprocessing.cpu_count()
    n_jobs = int(total_cores * 3 / 4)
    with Pool(n_jobs) as pool:
        # Check maybe this is passing everything and is not even a real speedup
        args = [(x, y) for x, y in list(itertools.product(source_rows, loaded_rows))]
        row_sim = list(pool.starmap(row_score, args))

    row_sim = np.asarray(row_sim)
    row_sim = np.reshape(row_sim, newshape=(len(source_rows), len(loaded_rows)))
    if np.max(row_sim):
        norm_row = row_sim / np.max(row_sim)
    else:
        norm_row = row_sim

    try:
        mwm = linear_sum_assignment(1 - norm_row)  # function minimizes weights
    except ValueError:
        import pdb
        pdb.set_trace()

    node_match = list(zip(mwm[0], mwm[1]))
    score = 0
    for i, j in node_match:
        score += row_sim[i, j]
    return score / len([v for x in source_rows for v in x])
    # node_diff = np.abs(np.diff(s0.shape)[0])


def deprecated_completeness(source_xml, loaded_xml):
    source_rows = [r.xpath("./cell[@role='header' or @role='data']") for r in source_xml.xpath("//row")]
    source_rows = [[normalize_cell(cell) for cell in r] for r in source_rows if len(r)]

    loaded_rows = [r.xpath("./cell") for r in loaded_xml.xpath("//row")]
    loaded_rows = [[normalize_cell(cell) for cell in r] for r in loaded_rows]
    # this is sensitive to row order and sensitive to column order

    score = 0
    start_row = 0
    for i, sr in enumerate(source_rows):
        max_score = 0
        for j in range(start_row, len(loaded_rows)):
            lr = loaded_rows[j]
            partial = row_score(sr, lr)
            if partial == len(sr) or (partial == len(lr)):
                max_score = partial
                start_row = j + 1
                break
            if partial > max_score:
                max_score = partial
                start_row = j + 1
        score += max_score

    try:
        return score / len([v for x in source_rows for v in x])
    except ZeroDivisionError:
        return -1


def completeness(source_xml, loaded_xml):
    source_rows = [r.xpath("./cell[@role='header' or @role='data']") for r in source_xml.xpath("//row")]
    source_rows = [[normalize_cell(cell) for cell in r] for r in source_rows if len(r)]
    source_cells = [c for row in source_rows for c in row]

    loaded_rows = [r.xpath("./cell") for r in loaded_xml.xpath("//row")]
    loaded_rows = [[normalize_cell(cell) for cell in r] for r in loaded_rows]
    loaded_cells = [c for row in loaded_rows for c in row]

    s = Multiset(source_cells)
    l = Multiset(loaded_cells)
    i = s.intersection(l)

    if len(source_cells) == 0:
        return 1.0
    elif not len(i):
        return 0.0
    else:
        return np.sum([v for k, v in i.items()]) / len(source_cells)


def conciseness(source_xml, loaded_xml):
    # source_rows = [r.xpath("./cell[@role='header' or @role='data']/value") for r in source_xml.xpath("//row")]
    # source_rows = [[v.text for v in r] for r in source_rows if len(r)]
    # loaded_rows = [r.xpath("./cell/value") for r in loaded_xml.xpath("//row")]
    # loaded_rows = [[v.text for v in r] for r in loaded_rows]  # this is sensitive to row order and sensitive to column order

    source_rows = [r.xpath("./cell[@role='header' or @role='data']") for r in source_xml.xpath("//row")]
    source_rows = [[normalize_cell(cell) for cell in r] for r in source_rows if len(r)]
    source_cells = [c for row in source_rows for c in row]

    loaded_rows = [r.xpath("./cell") for r in loaded_xml.xpath("//row")]
    loaded_rows = [[normalize_cell(cell) for cell in r] for r in loaded_rows]
    loaded_cells = [c for row in loaded_rows for c in row]

    s = Multiset(source_cells)
    l = Multiset(loaded_cells)
    i = s.intersection(l)

    if len(source_cells) == 0:
        return 1.0
    elif not len(i):
        return 0.0
    else:
        return np.sum([v for k, v in i.items()]) / len(loaded_cells)


def correctness(source_xml, loaded_xml):
    source_rows = [r.xpath("./cell[@role='header' or @role='data']") for r in source_xml.xpath("//row")]
    source_rows = [[normalize_cell(cell) for cell in r] for r in source_rows if len(r)]
    source_cells = [c for row in source_rows for c in row]

    loaded_rows = [r.xpath("./cell") for r in loaded_xml.xpath("//row")]
    loaded_rows = [[normalize_cell(cell) for cell in r] for r in loaded_rows]
    loaded_cells = [c for row in loaded_rows for c in row]

    pdb.set_trace()
    return 0
    s = Multiset(source_cells)
    l = Multiset(loaded_cells)
    i = s.intersection(l)

    if len(source_cells) == 0:
        return 1.0
    elif not len(i):
        return 0.0
    else:
        return np.sum([v for k, v in i.items()]) / len(loaded_cells)


def header_measures(source_xml, loaded_xml):
    source_rows = [r.xpath("./cell[@role='header']//value") for r in source_xml.xpath("//row")]
    # source_rows = [[normalize_cell(cell) for cell in r] for r in source_rows if len(r)]
    source_cells = [normalize_cell(c.text) for row in source_rows for c in row]
    loaded_rows = [r.xpath("./cell//value") for r in loaded_xml.xpath("//row[1]")] #TODO Rough measure
    # loaded_rows = [[normalize_cell(cell) for cell in r] for r in loaded_rows]
    loaded_cells = [normalize_cell(c.text) for row in loaded_rows for c in row]

    s = Multiset(source_cells)
    l = Multiset(loaded_cells)
    i = s.intersection(l)

    if len(source_cells) == 0:
        precision = recall = f1=  1.0
    elif not len(i):
        precision = recall = f1 = 0.0
    else:
        precision = np.sum([v for k, v in i.items()]) / len(source_cells)
        recall = np.sum([v for k, v in i.items()]) / len(loaded_cells)
        f1 = (precision * recall)/(precision+recall) *2

    return precision, recall, f1


def record_measures(source_xml, loaded_xml):
    source_rows = [r.xpath("./cell[@role='data']//value") for r in source_xml.xpath("//row")]
    source_rows = ["".join(map(lambda x: normalize_cell(x.text) or "null",lst_values)) for lst_values in source_rows if len(lst_values)]

    loaded_rows = [r.xpath("./cell//value") for r in loaded_xml.xpath("//row[position()>1]")]
    loaded_rows = ["".join(map(lambda x: normalize_cell(x.text) or "null",lst_values)) for lst_values in loaded_rows if len(lst_values)]

    s = Multiset(source_rows)
    l = Multiset(loaded_rows)
    i = s.intersection(l)

    if len(source_rows) == 0:
        precision = recall = f1=  1.0
    elif not len(i):
        precision = recall = f1 = 0.0
    else:
        precision = np.sum([v for k, v in i.items()]) / len(source_rows)
        recall = np.sum([v for k, v in i.items()]) / len(loaded_rows)
        f1 = (precision * recall)/(precision+recall) *2

    return precision, recall, f1

def cell_measures(source_xml, loaded_xml):

    source_rows = [r.xpath("./cell[@role='data']//value") for r in source_xml.xpath("//row")]
    # source_rows = [[normalize_cell(cell) for cell in r] for r in source_rows if len(r)]
    source_cells = [normalize_cell(c.text) for row in source_rows for c in row]

    loaded_rows = [r.xpath("./cell//value") for r in loaded_xml.xpath("//row[position()>1]")]
    # loaded_rows = [[normalize_cell(cell) for cell in r] for r in loaded_rows]
    loaded_cells = [normalize_cell(c.text) for row in loaded_rows for c in row]

    s = Multiset(source_cells)
    l = Multiset(loaded_cells)
    i = s.intersection(l)

    if len(source_cells) == 0:
        precision = recall = f1=  1.0
    elif not len(i):
        precision = recall = f1 = 0.0
    else:
        precision = np.sum([v for k, v in i.items()]) / len(source_cells)
        recall = np.sum([v for k, v in i.items()]) / len(loaded_cells)
        f1 = (precision * recall)/(precision+recall) *2

    return precision, recall, f1