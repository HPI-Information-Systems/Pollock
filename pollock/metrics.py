from __future__ import print_function
import builtins as __builtin__
from datetime import datetime
import numpy as np
import time
from multiset import Multiset

from .data_types import normalize_cell


def print(*args, **kwargs):
    return __builtin__.print(f"\033[94m{datetime.fromtimestamp(time.time() + 3600).strftime('%H:%M:%S')}:\033[0m", *args, **kwargs)


def successful(file_xml):
    if len([v.text for v in file_xml.xpath("//value") if v.text == "Application Error"]):
        return 0
    else:
        return 1


def row_score(source_row, target_row):
    s = Multiset(source_row)
    t = Multiset(target_row)
    i = s.intersection(t)
    return np.sum([v for k, v in i.items()])


def header_measures(source_xml, loaded_xml):
    source_rows = [r.xpath("./cell[@role='header']//value") for r in source_xml.xpath("//row")]
    source_cells = [normalize_cell(c.text) for row in source_rows for c in row]
    loaded_rows = [r.xpath("./cell//value") for r in loaded_xml.xpath("//row[1]")]
    loaded_cells = [normalize_cell(c.text) for row in loaded_rows for c in row]

    s = Multiset(source_cells)
    l = Multiset(loaded_cells)
    i = s.intersection(l)

    if len(source_cells) == 0:
        precision = recall = f1 = 1.0
    elif not len(i):
        precision = recall = f1 = 0.0
    else:
        precision = np.sum([v for k, v in i.items()]) / len(source_cells)
        recall = np.sum([v for k, v in i.items()]) / len(loaded_cells)
        f1 = (precision * recall) / (precision + recall) * 2

    return precision, recall, f1


def record_measures(source_xml, loaded_xml):
    source_rows = [r.xpath("./cell[@role='data']//value") for r in source_xml.xpath("//row")]
    source_rows = ["".join(map(lambda x: normalize_cell(x.text) or "null", lst_values)) for lst_values in source_rows if len(lst_values)]

    loaded_rows = [r.xpath("./cell//value") for r in loaded_xml.xpath("//row[position()>1]")]
    loaded_rows = ["".join(map(lambda x: normalize_cell(x.text) or "null", lst_values)) for lst_values in loaded_rows if len(lst_values)]

    s = Multiset(source_rows)
    l = Multiset(loaded_rows)
    i = s.intersection(l)

    if len(source_rows) == 0:
        precision = recall = f1 = 1.0
    elif not len(i):
        precision = recall = f1 = 0.0
    else:
        precision = np.sum([v for k, v in i.items()]) / len(source_rows)
        recall = np.sum([v for k, v in i.items()]) / len(loaded_rows)
        f1 = (precision * recall) / (precision + recall) * 2

    return precision, recall, f1


def cell_measures(source_xml, loaded_xml):
    source_rows = [r.xpath("./cell[@role='data']//value") for r in source_xml.xpath("//row")]
    source_cells = [normalize_cell(c.text) for row in source_rows for c in row]

    loaded_rows = [r.xpath("./cell//value") for r in loaded_xml.xpath("//row[position()>1]")]
    loaded_cells = [normalize_cell(c.text) for row in loaded_rows for c in row]

    s = Multiset(source_cells)
    l = Multiset(loaded_cells)
    i = s.intersection(l)

    if len(source_cells) == 0:
        precision = recall = f1 = 1.0
    elif not len(i):
        precision = recall = f1 = 0.0
    else:
        precision = np.sum([v for k, v in i.items()]) / len(source_cells)
        recall = np.sum([v for k, v in i.items()]) / len(loaded_cells)
        f1 = (precision * recall) / (precision + recall) * 2

    return precision, recall, f1
