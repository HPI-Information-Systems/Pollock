"""sieve - a CSV loader that works from the file's bytes alone.

    import sieve
    rows = sieve.load("data.csv")          # a path (str or os.PathLike)
    rows = sieve.load(b"a,b\\r\\n1,2\\r\\n")  # or the raw bytes (or a binary file object)

`load` returns a list of rows (lists of str). The first row is the header when the file has one;
a file without a header is returned as-is (no header is invented). Encoding, delimiter, quote and
escape characters, preamble, multi-row header, a trailing second table and damaged rows are all
decided from the file's content. A path is only used to open the file: nothing about its name
reaches the loader. Standard library only.

Command line: `python -m sieve file.csv` (or `sieve file.csv` once installed) writes the loaded
table to stdout as RFC-4180 CSV (comma, double quote, CRLF, UTF-8).
"""
import os

from . import loader as _loader

__version__ = "0.1.0"
__all__ = ["load", "load_bytes", "__version__"]


def load_bytes(data):
    """Load a CSV file given as bytes -> list of rows (list of str)."""
    return _loader.load(bytes(data))


def load(source):
    """Load a CSV file -> list of rows (list of str).

    `source` is a path (str or os.PathLike), bytes-like data, or a binary file object. A str is
    always a path; to load CSV text held in a str, pass `text.encode()`.
    """
    if isinstance(source, (bytes, bytearray, memoryview)):
        return load_bytes(source)
    if isinstance(source, (str, os.PathLike)):
        with open(source, "rb") as fh:
            return load_bytes(fh.read())
    read = getattr(source, "read", None)
    if read is not None:
        data = read()
        if isinstance(data, str):
            raise TypeError("sieve.load needs a binary file object (open the file with 'rb')")
        return load_bytes(data)
    raise TypeError(f"sieve.load expects a path, bytes or a binary file object, not {type(source).__name__}")
