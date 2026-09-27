"""Command line: python -m sieve FILE [-o OUT]

Loads FILE (or stdin when FILE is '-') with sieve.load and writes the table as normalised CSV:
comma delimiter, double quotes where needed (csv.QUOTE_MINIMAL), CRLF line ends, UTF-8.
"""
import argparse
import csv
import io
import sys

from . import __version__, load


def write_csv(rows, fh):
    """Write rows as RFC-4180 CSV to a text stream opened with newline=''."""
    csv.writer(fh).writerows(rows)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="sieve", description="Load a messy CSV file and write it "
                                 "back as normalised CSV (comma, double quote, CRLF, UTF-8).")
    ap.add_argument("file", help="input CSV file, or - for stdin")
    ap.add_argument("-o", "--output", help="output file (default: stdout)")
    ap.add_argument("--version", action="version", version=f"sieve {__version__}")
    a = ap.parse_args(argv)
    try:
        rows = load(sys.stdin.buffer.read() if a.file == "-" else a.file)
    except OSError as e:
        print(f"sieve: {e}", file=sys.stderr)
        return 1
    if a.output:
        with open(a.output, "w", newline="", encoding="utf-8") as fh:
            write_csv(rows, fh)
    else:
        out = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", newline="", write_through=True)
        try:
            write_csv(rows, out)
            out.flush()
        finally:
            out.detach()
    return 0


if __name__ == "__main__":
    sys.exit(main())
