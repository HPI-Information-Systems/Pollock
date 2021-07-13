import warnings
from dateutil.parser._parser import UnknownTimezoneWarning
warnings.simplefilter(action='ignore', category=UnknownTimezoneWarning)

import datetime
from backports.datetime_fromisoformat import MonkeyPatch
MonkeyPatch.patch_fromisoformat()

import re
import numpy as np
import dateutil.parser
import dateparser


class CellType():
    EMPTY = "TYPE_EMPTY" #0
    BOOLEAN = "TYPE_BOOLEAN" #1
    INTEGER = "TYPE_INT" #2
    FLOAT = "TYPE_FLOAT" #3
    TIME = "TYPE_TIME" #4
    DATE = "TYPE_DATE" #5
    STRING = "TYPE_STRING" #6


class customDateParserInfo(dateutil.parser.parserinfo):
    JUMP = [' ', '.', ',', ';', '-', '/', "'"]

def parse_cell(val, strip_comma = False):
    """ If stripping comma, strips comma to recognize integers, otherwise transforms them into full stops for floating points.
    """

    if not val.split() or val.isspace():
        return CellType.EMPTY
    try:
        if val in ["True","true","False","false"] or int(val) == 0 or int(val) ==1:
            return CellType.BOOLEAN
    except ValueError:
        pass

    val.replace(',','') if strip_comma else val.replace(',','.')

    try:
        int(val)
        return CellType.INTEGER
    except ValueError:
        pass
    try:
        float(val)
        return CellType.FLOAT
    except ValueError:
        pass
    try:
        datetime.time.fromisoformat(val)
        return CellType.TIME
    except ValueError:
        pass
    try:
        dateutil.parser.parse(val, parserinfo=customDateParserInfo())
        return CellType.DATE
    except ValueError:
        pass
    except TypeError:
        pass

    return CellType.STRING


def normalize_cell(cell):
    val = "".join([v.text or "" for v in cell if v.tag == "value"])

    typ = parse_cell(val, False)

    if typ == CellType.BOOLEAN:
        if val in ["False","false", "0", 0, 0.]:
            return 0
        elif val in ["True","true", "1", 1, 1.]:
            return 1

    elif typ == CellType.INTEGER:
        if val in ["NULL", "", "N/A"]:
            return 0
        else:
            return int(val)
    elif typ == CellType.FLOAT:
        return float(val)
    elif typ == CellType.DATE:
        return dateutil.parser.parse(val, parserinfo=customDateParserInfo())
    elif typ == CellType.TIME:
        return datetime.time.fromisoformat(val)
    else:
        return val.lower()
