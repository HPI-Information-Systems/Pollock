import warnings
from dateutil.parser._parser import UnknownTimezoneWarning
from pollock import timeparser #This module is not working on windows
from price_parser import Price

warnings.simplefilter(action='ignore', category=UnknownTimezoneWarning)

import dateutil.parser

class CellType():
    EMPTY = "TYPE_EMPTY"  # 0
    BOOLEAN = "TYPE_BOOLEAN"  # 1
    INTEGER = "TYPE_INT"  # 2
    FLOAT = "TYPE_FLOAT"  # 3
    TIME = "TYPE_TIME"  # 4
    DATE = "TYPE_DATE"  # 5
    STRING = "TYPE_STRING"  # 6
    CURRENCY = "TYPE_PRICE" #7


class customDateParserInfo(dateutil.parser.parserinfo):
    JUMP = [' ', '.', ',', ';', '-', '/', "'"]


def parse_cell(val, strip_comma=False):
    """ If stripping comma, strips comma to recognize integers, otherwise transforms them into full stops for floating points.
    """

    if not val.split() or val.isspace():
        return CellType.EMPTY
    try:
        if val in ["True", "true", "False", "false"] or int(val) == 0 or int(val) == 1:
            return CellType.BOOLEAN
    except ValueError:
        pass

    val.replace(',', '') if strip_comma else val.replace(',', '.')

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
        timeparser.parsetime(val)
        return CellType.TIME
    except ValueError:
        pass
    try:
        dateutil.parser.parse(val, parserinfo=customDateParserInfo())
        return CellType.DATE
    except (ValueError, OverflowError, TypeError) as e:
        pass
    price = Price.fromstring(val)
    if (price.currency is not None) and (price.amount is not None):
        return CellType.CURRENCY
    else:
        return CellType.STRING


def normalize_cell(cell):
    if cell is None or cell == "":
        return ""
    if type(cell) == type("string"):
        val = cell
    else:
        val = "".join([v.text or "" for v in cell if v.tag == "value"])

    typ = parse_cell(val, False)

    if typ == CellType.BOOLEAN:
        if val in ["False", "false", "0", 0, 0.]:
            return "0"
        elif val in ["True", "true", "1", 1, 1.]:
            return "1"
        else:
            return(str(bool(int(val))))

    elif typ == CellType.INTEGER:
        if val in ["NULL", "", "N/A"]:
            return "0"
        else:
            return str(int(val))
    elif typ == CellType.FLOAT:
        return str(float(val))
    elif typ == CellType.DATE:
        return str(dateutil.parser.parse(val, parserinfo=customDateParserInfo()))
    elif typ == CellType.TIME:
        return str(timeparser.parsetime(val))
    elif typ == CellType.CURRENCY:
        price = Price.fromstring(val)
        return price.currency+str(price.amount_float)
    else:
        return val.lower()
