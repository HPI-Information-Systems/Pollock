"""sieve's loader: bytes in, rows out.

Input: the file's bytes only. Output: list of rows (first row = header when the file has one;
a headerless file is emitted as-is, since no header is invented). The labels in parentheses
(c1, H2b, ...) name the experiment that introduced a stage; see EXPERIMENTS.md in
https://github.com/KenWuqianghao/sieve. Stages:
  1. decode   BOM sniff (utf-8/utf-16/32), else strict utf-8, else cp1252, else latin-1.
  2. dialect  grid over delimiter x quotechar x escapechar x skipinitialspace, each parsed with
              csv.reader on a sample and scored CleverCSV-style: Q = P * T, where P rewards
              many rows sharing few widths ((1/K) * sum_k N_k (L_k - 1) / L_k, K = number of
              distinct widths) and T is the share of cells matching a known type. Ties prefer
              the conventional choice (',', '"', no escape).
  3. structure  drop blank rows; drop a sparse preamble ended by a blank line; join a stack of
              leading header-like rows (multi-row header) with ' '; cut at the first blank-line-
              separated second table whose first row is header-like.
  4. row delimiter (c2)  a one-line record narrower than W under the file delimiter that splits
              quote-aware on another delimiter into >= W clean fields is re-split; surplus tokens
              merge into the columns this file's per-column shape profile says take that
              delimiter (a quoted token is a whole field); rewritten in the file dialect.
  5. stray quotes (c1)  find records whose QUOTING is broken - a strict-mode csv error (text
              after a closing quote) or spanning several physical lines where records normally
              take one - and re-parse the record's first physical line with one field-opening
              quote at a time treated as a literal character (kept in the cell). Accept the
              variant whose line comes out at exactly W (modal width) strict-clean fields and
              which lowers the number of broken records (wrong width or broken quoting) in the
              rest of the file. A clean one-line record of the wrong width is left alone.
  6. merged cells (c3)  a one-line record that lost one separator (narrower than W, or W wide
              only because a quoted field lost the separator before it) gets the one separator
              insertion whose W-field result fits this file's per-column profile (shape, first /
              last char class) uniquely best; a header-like first record only when exactly one
              insertion leaves no empty and no quote-bearing cell. Ties are left alone.
  gates (c4, H2b)  stages 4 and 6 touch a line only when (a) it does not start with a comment
              marker (#, //, %, --; the conventional comment prefixes of CSV-ish tools), (b) the
              target width W is the width of at least half of the file's non-blank records (a
              repair presumes a regular table with a rare damaged row; in a ragged file a
              short or long row is not evidence of damage), and (c) for a data row, the
              repaired row fits this file's per-column profile at least as well as the least
              typical of the file's own W-wide rows does, column by column on the columns the
              file's rows type (numbers, dates, codes...; leave-one-out); a file with no typed
              column (free text only) gives no evidence to check a repair against -> no repair.
  7. extra cells (c5, H4)  a one-line record exactly one cell wider than W that has an empty
              unquoted field: drop one such field (distinct results only). A data row takes the
              unique best under this file's per-column profile, every column's shape seen, and
              the stage-4/6 gates; a header-like first record (no profile) only when every drop
              gives the same row (one empty field, or adjacent empties).
Other ragged rows are emitted as parsed.
"""
import codecs
import csv
import functools
import io
import math
import re
from collections import Counter
from itertools import chain, compress

csv.field_size_limit(1 << 30)

DELIMS = [",", ";", "\t", "|", " ", ":"]
QUOTES = ['"', "'"]
ESCAPES = [None, "\\"]
SAMPLE = 1 << 16

_TYPES = [re.compile(p) for p in (
    r"^$",
    r"^[+-]?\d+$",
    r"^[+-]?(\d+[.,]\d*|\d*[.,]\d+)([eE][+-]?\d+)?$",
    r"^[+-]?\d{1,3}([,. ]\d{3})+([.,]\d+)?$",
    r"^[$€£¥]\s?[+-]?\d[\d,.]*$|^[+-]?\d[\d,.]*\s?[$€£¥%]$",
    r"^\d{1,4}[-/.]\d{1,2}[-/.]\d{1,4}$",
    r"^\d{1,2}:\d{2}(:\d{2})?(\s?[aApP][mM])?$",
    r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2})?",
    r"^(https?|ftp)://\S+$|^www\.\S+$",
    r"^[\w.+-]+@[\w-]+\.[\w.]+$",
    r"^(true|false|yes|no|null|nan|n/a|na)$",
    r"^[A-Za-z]{1,6}[-_]?\d+$",
    r"^[\w'&().,/ -]+$",  # plain words (CleverCSV counts alphanumeric text as a type too)
)]


def decode(data: bytes) -> str:
    for bom, enc in ((codecs.BOM_UTF32_LE, "utf-32"), (codecs.BOM_UTF32_BE, "utf-32"),
                     (codecs.BOM_UTF8, "utf-8-sig"), (codecs.BOM_UTF16_LE, "utf-16"),
                     (codecs.BOM_UTF16_BE, "utf-16")):
        if data.startswith(bom):
            return data.decode(enc, errors="replace")
    for enc in ("utf-8", "cp1252"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            pass
    return data.decode("latin-1")


def parse(text, delim, quote, esc, skipsp):
    return list(csv.reader(io.StringIO(text, newline=""), delimiter=delim, quotechar=quote,
                           escapechar=esc, doublequote=True, skipinitialspace=skipsp, strict=False))


_STRONG = re.compile("|".join(f"(?:{t.pattern})" for t in _TYPES[1:-1]))
_PLAIN = _TYPES[-1]


@functools.lru_cache(maxsize=1 << 16)
def strong(cell):
    """Typed as something other than empty / plain words (number, date, time, money, url, code...)."""
    c = cell.strip()
    return bool(_STRONG.match(c))


# empty | strong | plain in one regex; plain words first, as most typed cells match it early
# (the order of the alternatives cannot change whether one of them matches)
_ANY = re.compile("|".join(f"(?:{t.pattern})" for t in [_TYPES[-1]] + _TYPES[:-1]))


@functools.lru_cache(maxsize=1 << 16)
def typed(cell):
    # == (not c) or strong(c) or _PLAIN.match(c), in one regex pass
    return bool(_ANY.match(cell.strip()))


def dialect_score(rows):
    rows = [r for r in rows if r]
    if not rows:
        return 0.0
    widths = Counter(map(len, rows))
    p = sum(n * (w - 1) / w for w, n in widths.items()) / len(widths) / len(rows)
    # count distinct cell values once each (C-level Counter), then type each distinct value
    cells = Counter(chain.from_iterable(rows))
    n_cells = sum(widths[w] * w for w in widths)
    t = sum(compress(cells.values(), map(typed, cells))) / n_cells if n_cells else 0.0
    return p * t


def sniff(text):
    sample = text[:SAMPLE]
    if len(text) > SAMPLE:  # do not score a torn last line
        cut = max(sample.rfind("\n"), sample.rfind("\r"))
        sample = sample[:cut] if cut > 0 else sample
    best, best_q = (",", '"', None, False), -1.0
    # parses that cannot differ from one already scored are skipped (a tie never wins):
    # a second quote char when neither occurs in the sample, and skipinitialspace when no
    # field starts with a space
    both_quotes_absent = not any(q in sample for q in QUOTES)
    for d in DELIMS:
        if d not in sample:
            continue
        sp_matters = (d + " ") in sample or sample[:1] == " " or "\n " in sample or "\r " in sample
        for qi, q in enumerate(QUOTES):
            if qi and both_quotes_absent:
                continue
            for e in ESCAPES:
                if e is not None and e not in sample:
                    continue
                for sp in ((False, True) if d != " " and sp_matters else (False,)):
                    try:
                        s = dialect_score(parse(sample, d, q, e, sp))
                    except csv.Error:
                        continue
                    if s > best_q + 1e-9:  # strict: earlier (conventional) candidates win ties
                        best, best_q = (d, q, e, sp), s
    return best


def is_blank(r):
    # every cell whitespace-only  <=>  their concatenation is whitespace-only
    return not "".join(r).strip()


def header_like(row, below):
    """A row is header-like when its non-empty cells are untyped text while the rows below have
    typed values in most of those columns."""
    cells = [(i, c.strip()) for i, c in enumerate(row) if c.strip()]
    if not cells or not below:
        return False
    need = max(1, len(cells) // 2)
    hits, left = 0, len(cells)
    for i, c in cells:
        left -= 1
        # a typed cell never counts, so its column need not be looked at (same result, cheaper)
        if not strong(c):
            col = [v for v in (r[i].strip() for r in below if i < len(r)) if v]
            if col and sum(map(strong, col)) * 2 >= len(col):
                hits += 1
                if hits >= need:
                    return True
        if hits + left < need:
            return False
    return hits >= need


def structure(rows):
    # preamble: sparse rows at the top closed by a blank row
    for i in range(min(len(rows), 12)):
        if is_blank(rows[i]) and i > 0:
            above = rows[:i]
            width = max((len(r) for r in rows[i + 1:i + 20]), default=0)
            if all(sum(bool(c.strip()) for c in r) <= max(1, width // 2) for r in above):
                rows = rows[i + 1:]
            break
    rows = [r for r in rows if r and not is_blank(r)]
    # second table: a header-like row after some data rows -> keep the first table only
    start = 1
    while start < min(len(rows), 6) and header_like(rows[start], rows[start + 1:start + 40]):
        start += 1  # skip a multi-row header stack
    for i in range(start + 1, len(rows) - 1):
        if header_like(rows[i], rows[i + 1:i + 21]) and not header_like(rows[i - 1], rows[i + 1:i + 21]):
            rows = rows[:i]
            break
    # multi-row header: leading header-like rows stacked -> join column-wise with ' '
    k = 0
    while k < min(len(rows) - 1, 5) and header_like(rows[k], rows[k + 1:k + 40]):
        k += 1
    if k >= 2:
        # only rows that are header-like w.r.t. the data (not w.r.t. another header row)
        data = rows[k:k + 40]
        k = sum(1 for j in range(k) if header_like(rows[j], data))
    if k >= 2:
        width = max(len(r) for r in rows[:k])
        joined = [" ".join(r[i].strip() for r in rows[:k] if i < len(r) and r[i].strip())
                  for i in range(width)]
        rows = [joined] + rows[k:]
    return rows


# ---------------------------------------------------------------- stray-quote repair (c1)
MAX_REPAIRS = 20      # broken records examined per file (a file of many broken records is not
MAX_CANDIDATES = 16   # "one stray quote"; bounded cost), and quote positions tried per line
WINDOW = 200          # physical lines after a broken record over which a repair must help


def reader(lines, d, q, e, sp, strict=False):
    return csv.reader(iter(lines), delimiter=d, quotechar=q, escapechar=e, doublequote=True,
                      skipinitialspace=sp, strict=strict)


def records(lines, d, q, e, sp):
    """Non-strict parse of physical lines -> [(row, first_line, last_line)] (0-based)."""
    out = []
    r = reader(lines, d, q, e, sp)
    prev = 0
    for row in r:
        out.append((row, prev, r.line_num - 1))
        prev = r.line_num
    return out


def strict_ok(text_lines, d, q, e, sp):
    try:
        for _ in reader(text_lines, d, q, e, sp, strict=True):
            pass
        return True
    except csv.Error:
        return False


def modal(xs):
    counts = {}
    for x in xs:
        counts[x] = counts.get(x, 0) + 1
    return max(counts.items(), key=lambda kv: (kv[1], -kv[0]))[0] if counts else None


def target_width(lines, recs, d, q, e, sp):
    """Modal record width; if the records of that width cover under half of the physical lines
    (a stray quote near the top swallowed most of the file), the modal width of the lines
    parsed one by one."""
    widths = [len(r) for r, _, _ in recs if r and not is_blank(r)]
    w = modal(widths)
    covered = sum(b - a + 1 for r, a, b in recs if len(r) == w)
    if w is not None and covered * 2 >= len(lines):
        return w
    per_line = []
    for ln in lines:
        rows = list(reader([ln], d, q, e, sp))
        if len(rows) == 1 and not is_blank(rows[0]):
            per_line.append(len(rows[0]))
    return modal(per_line) or w


def quote_broken(rec, lines, multi_line_rare, d, q, e, sp):
    """Evidence that quoting (not separators) broke this record: it spans several physical lines
    in a file whose records take one, or its text fails a strict csv parse (text after a closing
    quote). A single-line record of the wrong width that parses cleanly is a separator problem
    (merged / extra cell), which quote repair must not touch."""
    row, a, b = rec
    if not row or is_blank(row):
        return False
    if b > a and multi_line_rare:
        return True
    seg = lines[a:b + 1]
    return any(q in ln for ln in seg) and not strict_ok(seg, d, q, e, sp)


def broken(rec, lines, w, multi_line_rare, d, q, e, sp):
    row = rec[0]
    if row and not is_blank(row) and len(row) != w:
        return True
    return quote_broken(rec, lines, multi_line_rare, d, q, e, sp)


def field_quote_positions(line, d, q, sp):
    """Positions of quote characters that open a field (line start or after a delimiter)."""
    out = []
    for p, ch in enumerate(line):
        if ch != q:
            continue
        k = p - 1
        if sp:
            while k >= 0 and line[k] == " ":
                k -= 1
        if k < 0 or line[k] == d:
            out.append(p)
    return out


def literalise(line, p, q, ph):
    """The quote at p is a stray literal character of the field it opens. If the field was quoted
    already (the next char is the quote char), keep that opening quote and put the literal inside
    it; otherwise the field becomes unquoted and starts with the literal."""
    if line[p + 1:p + 2] == q:
        return line[:p] + q + ph + line[p + 2:]
    return line[:p] + ph + line[p + 1:]


def repair_stray_quotes(text, d, q, e, sp):
    # physical lines exactly as the csv module sees them (\r, \n, \r\n only; str.splitlines
    # would also split on \x0b, \x0c, \x1c-\x1e, \x85, \u2028, \u2029)
    lines = list(io.StringIO(text, newline=""))
    if not lines or q not in text:
        return text, None
    recs = records(lines, d, q, e, sp)
    w = target_width(lines, recs, d, q, e, sp)
    if w is None:
        return text, None
    spans = [b - a for _, a, b in recs]
    multi_line_rare = sum(1 for s in spans if s == 0) >= 0.9 * len(spans)
    ph = next(chr(c) for c in range(0xE000, 0xF8FF) if chr(c) not in text)

    def n_broken(rs, limit):
        # broken records starting before `limit` (a window after the record under repair keeps
        # the cost linear; a swallowed record that ran to the end still starts inside it)
        return sum(broken(r, lines, w, multi_line_rare, d, q, e, sp) for r in rs if r[1] < limit)

    changed = False
    tried = 0
    ri = 0
    while ri < len(recs) and tried < MAX_REPAIRS:
        rec = recs[ri]
        if not quote_broken(rec, lines, multi_line_rare, d, q, e, sp):
            ri += 1
            continue
        tried += 1
        a = rec[1]
        line = lines[a]
        limit = rec[2] + 1 + WINDOW
        old_bad = n_broken(recs[ri:], limit)
        best = None
        for p in field_quote_positions(line, d, q, sp)[:MAX_CANDIDATES]:
            fixed = literalise(line, p, q, ph)
            one = list(reader([fixed], d, q, e, sp, strict=True)) if strict_ok([fixed], d, q, e, sp) else None
            if not one or len(one) != 1 or len(one[0]) != w:
                continue
            saved = lines[a]
            lines[a] = fixed
            new_suffix = [(r, x + a, y + a) for r, x, y in records(lines[a:], d, q, e, sp)]
            bad = n_broken(new_suffix, limit)
            lines[a] = saved
            if bad < old_bad and (best is None or bad < best[0]):
                best = (bad, fixed, new_suffix)
        if best is None:
            ri += 1
            continue
        lines[a] = best[1]
        recs = recs[:ri] + best[2]
        changed = True
        ri += 1
    if not changed:
        return text, None
    return "".join(lines), ph


# ---------------------------------------------------------------- repair gates (c4, H2b)
COMMENT_MARKERS = ("#", "//", "%", "--")  # conventional comment prefixes (R, pandas, DuckDB
                                          # `comment=`, ARFF / MATLAB, C / SQL style notes)
MIN_WIDTH_SHARE = 0.5  # W must be the width of at least half of the non-blank records

_trace = None  # analysis hook: a list to append gate decisions to (None in normal use)


def _log(*a):
    if _trace is not None:
        _trace.append(a)


def comment_line(line):
    """The physical line starts (after blanks / a BOM) with a comment marker: free text by
    convention, never a damaged record."""
    return line.lstrip(" \t\ufeff").startswith(COMMENT_MARKERS)


def width_dominant(recs, w):
    """A row repair presumes a regular table: W is the width of most records. In a file where
    it is not (ragged lists, space-aligned text), an odd width is not evidence of damage."""
    rs = [r for r, _, _ in recs if r and not is_blank(r)]
    return bool(rs) and sum(len(r) == w for r in rs) >= MIN_WIDTH_SHARE * len(rs)


# ---------------------------------------------------------------- per-row delimiter (c2)
MIN_PROFILE_ROWS = 5  # good rows needed before a column profile counts as evidence
ALPHA = 0.5           # additive smoothing of the per-column shape frequencies


def tokenize(line, d, q, e):
    """Quote-aware split of ONE physical line on d -> [(value, was_quoted)], or None when the
    line does not parse cleanly (unterminated quote, text after a closing quote)."""
    line = line.rstrip("\r\n")
    out, i, n = [], 0, len(line)
    while True:
        if i < n and line[i] == q:
            i += 1
            buf = []
            while True:
                # jump to the next quote (or escape) instead of walking char by char
                j = line.find(q, i)
                if e:
                    k = line.find(e, i)
                    if k >= 0 and (j < 0 or k < j) and k + 1 < n:
                        buf.append(line[i:k])
                        buf.append(line[k + 1])
                        i = k + 2
                        continue
                if j < 0:
                    return None
                buf.append(line[i:j])
                if line[j + 1:j + 2] == q:
                    buf.append(q)
                    i = j + 2
                    continue
                i = j + 1
                break
            if i < n and line[i] != d:
                return None
            out.append(("".join(buf), True))
        else:
            j = line.find(d, i)
            j = n if j < 0 else j
            out.append((line[i:j], False))
            i = j
        if i >= n:
            return out
        i += 1  # the delimiter
        if i == n:
            out.append(("", False))
            return out


@functools.lru_cache(maxsize=1 << 16)
def shape(cell, dp):
    """Coarse shape class of a cell: empty, one of the typed patterns, or plain / other text,
    split by whether the text contains dp (the delimiter the odd row uses)."""
    c = cell.strip()
    if not c:
        return "empty"
    for k, t in enumerate(_TYPES[1:-1], 1):
        if t.match(c):
            return k
    return ("words" if dp in c else "word") if _PLAIN.match(c) else ("other+" if dp in c else "other")


def column_profiles(rows, w, dp):
    """Per-column shape counts over the rows of width w (this file only)."""
    prof = [{} for _ in range(w)]
    n = 0
    for r in rows:
        if len(r) != w:
            continue
        n += 1
        for j, v in enumerate(r):
            s = shape(v, dp)
            prof[j][s] = prof[j].get(s, 0) + 1
    return prof, n


def fit_tokens(tokens, w, prof, n, dp):
    """Assign the tokens, in order, to w columns (consecutive groups joined by dp). A quoted token
    is a whole field (csv semantics), so it is never merged with a neighbour. Score = sum of
    log smoothed P(shape | column) from this file's profile; dynamic programme over the split
    points. Returns (score, number_of_optimal_splits, groups, unseen_columns) or None."""
    T = len(tokens)
    if T < w:
        return None
    k = 1 + len({s for p in prof for s in p})
    NEG = float("-inf")
    best = [[NEG] * (T + 1) for _ in range(w + 1)]
    cnt = [[0] * (T + 1) for _ in range(w + 1)]
    arg = [[0] * (T + 1) for _ in range(w + 1)]
    best[0][0], cnt[0][0] = 0.0, 1
    joins, lg = {}, {}

    def joined(a, b):
        if (a, b) not in joins:
            joins[(a, b)] = dp.join(t[0] for t in tokens[a:b])
        return joins[(a, b)]

    def col_score(j, a, b):
        if b - a > 1 and any(tokens[x][1] for x in range(a, b)):
            return None
        s = shape(joined(a, b), dp)
        if (j, s) not in lg:
            lg[(j, s)] = math.log((prof[j].get(s, 0) + ALPHA) / (n + ALPHA * k))
        return lg[(j, s)]

    for j in range(1, w + 1):
        for b in range(j, T - (w - j) + 1):
            for a in range(j - 1, b):
                if best[j - 1][a] == NEG:
                    continue
                s = col_score(j - 1, a, b)
                if s is None:
                    continue
                v = best[j - 1][a] + s
                if v > best[j][b] + 1e-9:
                    best[j][b], cnt[j][b], arg[j][b] = v, cnt[j - 1][a], a
                elif abs(v - best[j][b]) <= 1e-9:
                    cnt[j][b] += cnt[j - 1][a]
    if best[w][T] == NEG:
        return None
    groups, b = [], T
    for j in range(w, 0, -1):
        a = arg[j][b]
        groups.append(joined(a, b))
        b = a
    groups.reverse()
    unseen = sum(1 for j, g in enumerate(groups) if prof[j].get(shape(g, dp), 0) == 0)
    return best[w][T], cnt[w][T], groups, unseen


def n_admissible(tokens, w):
    """Number of ways to cut the tokens into w consecutive groups when a quoted token must stand
    alone (the split count when no profile can arbitrate, e.g. for a header)."""
    T = len(tokens)
    ways = [[0] * (T + 1) for _ in range(w + 1)]
    ways[0][0] = 1
    for j in range(1, w + 1):
        for b in range(j, T + 1):
            ways[j][b] = sum(ways[j - 1][a] for a in range(j - 1, b)
                             if b - a == 1 or not any(tokens[x][1] for x in range(a, b)))
    return ways[w][T]


def serialise(row, line, d, q, e):
    """One record in the file's own dialect, keeping the physical line's terminator."""
    term = line[len(line.rstrip("\r\n")):]
    buf = io.StringIO()
    csv.writer(buf, delimiter=d, quotechar=q, escapechar=e, doublequote=True,
               quoting=csv.QUOTE_MINIMAL, lineterminator=term).writerow(row)
    return buf.getvalue()


def repair_row_delimiters(text, d, q, e, sp):
    """A one-line record that is narrower than the file's width W under the file delimiter d, but
    splits quote-aware on another delimiter dp into >= W clean fields none of which (unquoted)
    contains d, is a row written in its own dialect. Its tokens are assigned to the W columns by
    this file's per-column shape profile (surplus tokens merge, joined by dp, into the columns
    whose values take dp - free text); the record is rewritten in the file dialect. Gates: a data
    row must fit the profile (at most one column gets a shape never seen in that column); the
    first record (a header has no profile) needs exactly one admissible split, a W-wide record
    after it, and must look like a header against the rows below."""
    lines = list(io.StringIO(text, newline=""))
    if not lines:
        return text
    recs = records(lines, d, q, e, sp)
    w = target_width(lines, recs, d, q, e, sp)
    if w is None or w < 3 or not width_dominant(recs, w):
        return text
    profs, good, tprof = {}, None, None
    first = next((i for i, (r, _, _) in enumerate(recs) if r and not is_blank(r)), None)
    changed, ri, fixes = False, 0, 0
    while ri < len(recs) and fixes < MAX_REPAIRS:
        row, a, _ = recs[ri]
        if not row or is_blank(row) or len(row) >= w or comment_line(lines[a]):
            ri += 1
            continue
        line = lines[a]
        best = None
        for dp in DELIMS:
            if dp == d or dp not in line:
                continue
            toks = tokenize(line, dp, q, e)
            if not toks or len(toks) < w or any(d in v for v, quoted in toks if not quoted):
                continue
            if good is None:
                good = [r for r, _, _ in recs if len(r) == w][1:]
            if dp not in profs:
                profs[dp] = column_profiles(good, w, dp)
            prof, n = profs[dp]
            if n < MIN_PROFILE_ROWS:
                continue
            fit = fit_tokens(toks, w, prof, n, dp)
            if fit is None:
                continue
            score, ties, groups, unseen = fit
            if ri == first:
                nxt = recs[ri + 1][0] if ri + 1 < len(recs) else None
                if n_admissible(toks, w) != 1 or not nxt or len(nxt) != w or not header_like(groups, good[:40]):
                    continue
            elif unseen > 1:
                continue
            else:
                if tprof is None:
                    tprof = Profile(good, w)
                if not tprof.typical(groups, good):
                    _log("H2", "atypical", ri, groups)
                    continue
            if best is None or score > best[0]:
                best = (score, groups)
        if best is None:
            ri += 1
            continue
        lines[a] = serialise(best[1], line, d, q, e)
        recs = recs[:ri] + [(r, x + a, y + a) for r, x, y in records(lines[a:], d, q, e, sp)]
        changed = True
        fixes += 1
        ri += 1
    return "".join(lines) if changed else text


# ---------------------------------------------------------------- merged cells (c3)
MAX_LINE = 4096       # longest physical line tried for a missing-separator split


def char_class(ch):
    if ch.isdigit():
        return "9"
    if ch.isalpha():
        return "A" if ch.isupper() else "a"
    return "s" if ch.isspace() else ch


@functools.lru_cache(maxsize=1 << 16)
def cell_features(v):
    """Naive-Bayes features of one cell: shape class, first and last character class."""
    c = v.strip()
    if not c:
        return ("empty", "", "")
    return (shape(v, " "), char_class(c[0]), char_class(c[-1]))


class Profile:
    """Per-column feature counts over the rows of width w (this file only)."""

    def __init__(self, rows, w):
        self.w, self.n = w, 0
        self.counts = [[{}, {}, {}] for _ in range(w)]
        rs = [r for r in rows if len(r) == w]
        self.n = len(rs)
        for j in range(w):
            # count each distinct value once (only the counts are used, never their order)
            cj = self.counts[j]
            for v, m in Counter(r[j] for r in rs).items():
                for k, f in enumerate(cell_features(v)):
                    cj[k][f] = cj[k].get(f, 0) + m

    def score(self, row):
        """(sum of log smoothed P(feature | column), columns whose shape was never seen there)."""
        s, unseen = 0.0, 0
        for j, v in enumerate(row):
            for k, f in enumerate(cell_features(v)):
                c = self.counts[j][k]
                s += math.log((c.get(f, 0) + ALPHA) / (self.n + ALPHA * (len(c) + 1)))
                if k == 0 and f not in c:
                    unseen += 1
        return s, unseen

    def floors(self, rows):
        """Typed columns (at least half of the file's own W-wide values typed: numbers, dates,
        codes, money, urls...) and, per typed column, the leave-one-out score of its least
        typical ordinary cell (each cell scored against the other rows' counts)."""
        if getattr(self, "_floors", None) is None:
            rs = [r for r in rows if len(r) == self.w]
            m = self.n - 1
            fl = {}
            for j in range(self.w):
                if not rs or sum(strong(r[j]) for r in rs) * 2 < len(rs):
                    continue
                lo = float("inf")
                # the leave-one-out score depends only on the cell's features: score each
                # distinct feature triple once
                for feats in {cell_features(r[j]) for r in rs}:
                    s = 0.0
                    for k, f in enumerate(feats):
                        c = self.counts[j][k]
                        cf = c[f] - 1
                        distinct = len(c) - (1 if cf == 0 else 0)
                        s += math.log((cf + ALPHA) / (m + ALPHA * (distinct + 1)))
                    lo = min(lo, s)
                fl[j] = lo
            self._floors = fl
        return self._floors

    def cell_score(self, j, v):
        s = 0.0
        for k, f in enumerate(cell_features(v)):
            c = self.counts[j][k]
            s += math.log((c.get(f, 0) + ALPHA) / (self.n + ALPHA * (len(c) + 1)))
        return s

    def typical(self, row, rows):
        """The repaired row fits this file's columns at least as well as the file's own rows do:
        in every typed column its cell scores at least as well as that column's least typical
        ordinary cell. A file without a typed column gives no evidence to check a repair
        against (free text only), so nothing is repaired there."""
        fl = self.floors(rows)
        return bool(fl) and all(self.cell_score(j, row[j]) >= lo - 1e-9 for j, lo in fl.items())


def one_record(line, d, q, e, sp):
    try:
        rows = list(reader([line], d, q, e, sp, strict=True))
    except csv.Error:
        return None
    return rows[0] if len(rows) == 1 else None


def unquoted_quote(line, d, q, e):
    """The line parses cleanly and one of its unquoted fields contains the quote char: a quoted
    field that lost the separator in front of it (the quote no longer opens the field)."""
    toks = tokenize(line, d, q, e)
    return bool(toks) and any(q in v for v, quoted in toks if not quoted)


def repair_merged_cells(text, d, q, e, sp):
    """A one-line record that lost one separator: narrower than W, or W wide only because a
    quoted field lost the separator in front of it (its quote is now mid-field, so the
    separators inside it split). Every insertion point of one separator that gives a strict-clean
    W-field record is a candidate; candidates are scored against this file's per-column profile
    (shape, first / last character class). Accept the unique best when every column's shape has
    been seen in that column (and, for a W-wide record, it beats the record as parsed). The first
    record, when header-like, has no profile: accept only when exactly one candidate has no
    empty cell and no quote character. Ties are left alone."""
    lines = list(io.StringIO(text, newline=""))
    if not lines:
        return text
    recs = records(lines, d, q, e, sp)
    w = target_width(lines, recs, d, q, e, sp)
    if w is None or w < 3 or not width_dominant(recs, w):
        return text
    good = [r for r, _, _ in recs if len(r) == w][1:]
    if len(good) < MIN_PROFILE_ROWS:
        return text
    prof = None
    first = next((i for i, (r, _, _) in enumerate(recs) if r and not is_blank(r)), None)
    changed, tried = False, 0
    for ri, (row, a, b) in enumerate(recs):
        if tried >= MAX_REPAIRS:
            break
        if not row or is_blank(row) or a != b or len(lines[a]) > MAX_LINE or comment_line(lines[a]):
            continue
        line = lines[a]
        if len(row) == w and not (q in line and unquoted_quote(line, d, q, e)):
            continue
        if len(row) > w and q not in line:  # only a quote can make an insertion narrow a row
            continue
        tried += 1
        body = line.rstrip("\r\n")
        term = line[len(body):]
        cands = {}
        pad = " " if sp else ""
        for p in range(len(body) + 1):
            # a wider record can only narrow if the separator lets a mid-field quote open a field
            if len(row) > w and not body[p:].lstrip(pad).startswith(q):
                continue
            cand = body[:p] + d + body[p:]
            r = one_record(cand, d, q, e, sp)
            if r is not None and len(r) == w:
                cands.setdefault(tuple(r), cand)
        if not cands:
            continue
        if ri == first and header_like(row, good[:40]):
            ok = [v for v in cands if all(x.strip() for x in v) and not any(q in x for x in v)]
            if len(ok) != 1:
                continue
            pick = ok[0]
        else:
            if prof is None:
                prof = Profile(good, w)
            scored = sorted(((prof.score(v), v) for v in cands), key=lambda t: -t[0][0])
            (top, unseen), pick = scored[0]
            if unseen or (len(scored) > 1 and scored[1][0][0] >= top - 1e-9):
                continue
            if len(row) == w and prof.score(row)[0] >= top:
                continue
            if not prof.typical(pick, good):
                _log("H3", "atypical", ri, pick)
                continue
        lines[a] = cands[pick] + term
        changed = True
    return "".join(lines) if changed else text


# ---------------------------------------------------------------- extra cells (c5, H4)
def repair_extra_cells(text, d, q, e, sp):
    """A one-line record one cell wider than W with an empty unquoted field got one separator too
    many: the extra separator leaves an empty field behind. Candidates = the row without one of
    its empty unquoted fields (distinct rows only: dropping either of two adjacent empties gives
    the same row). A data row takes the candidate that fits this file's per-column profile
    uniquely best, with every column's shape seen there and the typicality gate; the first
    record, when header-like (no profile for a header), only when all candidates coincide.
    Same comment / dominant-width gates as the other separator repairs. Ties are left alone."""
    lines = list(io.StringIO(text, newline=""))
    if not lines:
        return text
    recs = records(lines, d, q, e, sp)
    w = target_width(lines, recs, d, q, e, sp)
    if w is None or w < 3 or not width_dominant(recs, w):
        return text
    good = [r for r, _, _ in recs if len(r) == w][1:]
    if len(good) < MIN_PROFILE_ROWS:
        return text
    prof = None
    first = next((i for i, (r, _, _) in enumerate(recs) if r and not is_blank(r)), None)
    changed, tried = False, 0
    for ri, (row, a, b) in enumerate(recs):
        if tried >= MAX_REPAIRS:
            break
        if len(row) != w + 1 or a != b or len(lines[a]) > MAX_LINE or comment_line(lines[a]):
            continue
        toks = tokenize(lines[a], d, q, e)
        if not toks or len(toks) != len(row):
            continue
        empties = [j for j, (v, quoted) in enumerate(toks) if v == "" and not quoted]
        if not empties:
            continue
        tried += 1
        cands = []
        for j in empties:
            c = tuple(row[:j] + row[j + 1:])
            if c not in cands:
                cands.append(c)
        if ri == first and any(header_like(list(c), good[:40]) for c in cands):
            if len(cands) != 1:
                _log("H4", "header ambiguous", ri, cands)
                continue
            pick = cands[0]
        else:
            if prof is None:
                prof = Profile(good, w)
            scored = sorted(((prof.score(c), c) for c in cands), key=lambda t: -t[0][0])
            (top, unseen), pick = scored[0]
            if unseen or (len(scored) > 1 and scored[1][0][0] >= top - 1e-9):
                _log("H4", "tie or unseen", ri, pick)
                continue
            if not prof.typical(pick, good):
                _log("H4", "atypical", ri, pick)
                continue
        new = serialise(list(pick), lines[a], d, q, e)
        if one_record(new.rstrip("\r\n"), d, q, e, sp) != list(pick):
            continue  # the file dialect cannot write this row back unchanged
        lines[a] = new
        changed = True
    return "".join(lines) if changed else text


def load(data: bytes):
    # the type caches are per file: every Pollock file is a variant of the same table, so a
    # cross-file cache would inflate throughput with content memorised from other files
    strong.cache_clear()
    typed.cache_clear()
    shape.cache_clear()
    cell_features.cache_clear()
    if not data:
        return []
    text = decode(data)
    d, q, e, sp = sniff(text)
    text = repair_row_delimiters(text, d, q, e, sp)
    text, ph = repair_stray_quotes(text, d, q, e, sp)
    text = repair_merged_cells(text, d, q, e, sp)
    text = repair_extra_cells(text, d, q, e, sp)
    rows = parse(text, d, q, e, sp)
    if ph:
        rows = [[c.replace(ph, q) if ph in c else c for c in r] for r in rows]
    return structure(rows)
