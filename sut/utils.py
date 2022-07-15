import builtins as __builtin__
from datetime import datetime
from time import time

def parse_utf(filename, pollution):
    """
    Convenience function to split for example "table_field_delimiter_0x20.csv" into the string "," to feed as a parameter.
    :param filename: the filename containing a pollution, a set of unicode characters in hex-string form delimited with underscore
    :param pollution: the pollution to isolate
    :return: the string joined parsing the utf characters
    """
    arr = filename.split(pollution)[1][:-4]
    s = "".join([chr(int(d, 0)) for d in arr.split("_")])
    return s

def print(*args, **kwargs):
    """
    Custom print functions that outputs the timestamp (in local computer time)
    :param args:
    :param kwargs:
    :return:
    """
    return __builtin__.print(f'\033[94m{datetime.fromtimestamp(time() + 3600).strftime("%H:%M:%S")}:\033[0m', *args,
                             **kwargs)
