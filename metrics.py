from __future__ import print_function
import builtins as __builtin__
import itertools
import multiprocessing
from datetime import datetime
import numpy as np
import time
from multiset import Multiset

from scipy.optimize import linear_sum_assignment
from multiprocessing.pool import Pool

from data_types import normalize_cell


def print(*args, **kwargs):
    return __builtin__.print(f"\033[94m{datetime.fromtimestamp(time.time()+3600).strftime('%H:%M:%S')}:\033[0m", *args, **kwargs)

def successful(file_xml):
    if len([v.text for v in file_xml.xpath("//value") if v.text == "Application Error"]):
        return 0
    else:
        return 1

def completeness(source_xml, loaded_xml):
    source_rows =[r.xpath("./cell[@role='header' or @role='data']") for r in source_xml.xpath("//row")]
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
        return np.sum([v for k,v in i.items()])/len(source_cells)

def conciseness(source_xml, loaded_xml):

    source_rows =[r.xpath("./cell[@role='header' or @role='data']") for r in source_xml.xpath("//row")]
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
        return np.sum([v for k,v in i.items()])/len(loaded_cells)