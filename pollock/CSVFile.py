import regex as re
import csv
import os
import sys
from pathlib import Path
import json as json 

import chardet
from clevercsv.cparser_util import parse_string
from clevercsv.dialect import SimpleDialect
from joblib import Parallel, delayed
from lxml import etree
from lxml.builder import E

from .data_types import parse_cell, normalize_cell

CSV_XSL = '''<xsl:stylesheet version="3.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"> <xsl:output method="text" /> 
<xsl:template match="/">
    <xsl:for-each select="//row">
        <xsl:for-each select="child::*">
            <xsl:value-of select="."/>
        </xsl:for-each>
    </xsl:for-each>
</xsl:template>
</xsl:stylesheet>'''

csv.field_size_limit(min(sys.maxsize, 2147483646))

def create_row(row: list, role: str, field_delimiter: str, quotation_char: str, escape_char: str, record_delimiter: str, normalize=False):
    """This function is used to create a row element to be inserted in a files' XML
    """
    r = E.row(role=role)
    n_cells = len(row)
    for j, (cell, is_quoted) in enumerate(row):
        typ = parse_cell(cell)
        cell_text = cell
        if j > 0 and len(field_delimiter) > 1:
            cell_text = cell_text[1:]

        c = create_cell(field_delimiter, quotation_char, escape_char, text=cell_text, role=role, type=typ, should_quote=is_quoted,
                        normalize=normalize)
        r.append(c)

        if j < n_cells - 1:
            delimiter = E.field_delimiter(field_delimiter)
            r.append(delimiter)

    row_delimiter = E.record_delimiter(record_delimiter)
    r.append(row_delimiter)
    return etree.tostring(r)


def create_cell(field_delimiter: str, quotation_char: str, escape_char: str, text: str, should_quote=False, role: str = None, normalize=False,
                **kwargs):
    """This function is used to create a cell element to be inserted in a files' XML,
        respecting quotation and escape characters.
        Keyword arguments are used as attributes in the resulting element.
        should_quote is used in case in the original file the cell was quoted regardless
    """
    cell = etree.Element("cell", role=role, **kwargs)

    to_quote = (text or '').find(field_delimiter) > 0
    if to_quote or should_quote:
        q = etree.SubElement(cell, "quotation_char")
        q.text = quotation_char

    values = text.split(quotation_char)
    for vdx, v in enumerate(values):
        v_text = normalize_cell(v) if normalize else v
        v_text = re.sub(r'\p{Cc}', '', v_text)
        if vdx == 0:
            cell.append(E.value(v_text))
        else:
            cell.append(E.escape_char(escape_char))
            cell.append(E.value(quotation_char + v_text))

    if to_quote or should_quote:
        q = etree.SubElement(cell, "quotation_char")
        q.text = quotation_char

    return cell


class CSVFile:
    """This class is used to load a CSV file and record it as an XML tree
    """

    def __init__(self, filename, parameters: dict = None,
                 record_delimiter="\r\n",
                 field_delimiter=",",
                 quotation_char='"',
                 escape_char='"',
                 preamble_rows=0,
                 no_header=False,
                 header_lines=1,
                 quote_all=False,
                 n_jobs=1,
                 normalize=False,
                 skip_xml=False):

        self.filename = filename.split("/")[-1]
        root = etree.Element("file", filename=self.filename)
        self.size_kb = os.path.getsize(filename) / 1024
        if self.size_kb == 0:
            self.xml = etree.ElementTree(root)
            return

        if parameters is not None:
            self.encoding = parameters["encoding"]
            self.field_delimiter = parameters["delimiter"]
            self.record_delimiter = parameters["record_delimiter"]
            self.quotation_char = parameters["quotechar"]
            self.escape_char = parameters["escapechar"]
            self.preamble_rows = parameters["preamble_rows"]
            self.no_header = parameters["no_header"]
            self.header_lines = parameters["header_lines"]
        else:
            self.field_delimiter = field_delimiter
            self.record_delimiter = record_delimiter
            self.quotation_char = quotation_char
            self.escape_char = escape_char
            self.preamble_rows = preamble_rows
            self.no_header = no_header
            self.header_lines = header_lines

        if skip_xml:
            self.xml = None
            return

        with open(filename, 'rb') as rawfile:
            rawdata = rawfile.read()

        try:
            data = rawdata.decode(self.encoding)
        except Exception as e:
            result = chardet.detect(rawdata)
            self.encoding = result["encoding"]
            data = rawdata.decode(self.encoding)

        root.attrib["encoding"] = self.encoding
        table = etree.SubElement(root, "table")
        self.quote_all = quote_all
        dict_roles = {}
        for idx in range(self.preamble_rows):
            dict_roles[idx] = "preamble"
        for idx in range(self.preamble_rows, self.preamble_rows + self.header_lines):
            dict_roles[idx] = "header"

        if self.escape_char == self.quotation_char:
            dialect = SimpleDialect(self.field_delimiter[0], self.quotation_char, escapechar='')
        else:
            dialect = SimpleDialect(self.field_delimiter[0], self.quotation_char, self.escape_char)
        lst_rows = list(parse_string(data, dialect, return_quoted=True))

        self.row_count = len(lst_rows)
        try:
            self.col_count = max([len(row) for row in lst_rows])
        except ValueError:
            self.col_count = 0
        if n_jobs == 1 or self.row_count < 10000:
            xml_rows = list(map(lambda x: create_row(row=x[1],
                                                     role=dict_roles.get(x[0], "data"),
                                                     field_delimiter=self.field_delimiter,
                                                     quotation_char=self.quotation_char,
                                                     escape_char=self.escape_char,
                                                     record_delimiter=self.record_delimiter,
                                                     normalize=normalize),
                                enumerate(lst_rows)))
        else:
            args = [{"row": row, "role": dict_roles.get(idx, "data"),
                     "field_delimiter": self.field_delimiter,
                     "quotation_char": self.quotation_char,
                     "escape_char": self.escape_char,
                     "record_delimiter": self.record_delimiter,
                     "normalize": normalize}
                    for idx, row in enumerate(lst_rows)]
            with Parallel(n_jobs=n_jobs, verbose=0) as parallel:
                xml_rows = parallel(delayed(create_row)(**arg) for arg in args)


        [table.append(etree.fromstring(row)) for row in xml_rows]

        self.xml = etree.ElementTree(root)

    def write_csv(self, out_path="./", verbose=False):
        xslt = etree.XML(CSV_XSL)
        transform = etree.XSLT(xslt)
        output = transform(self.xml)

        if verbose:
            print("\n" + str(output))
        Path(out_path).mkdir(parents=True, exist_ok=True)
        with open(out_path + self.filename, "w", encoding=self.encoding) as out:
            out.write(str(output))

    def write_xml(self, out_path="./", pretty=False):
        Path(out_path).mkdir(parents=True, exist_ok=True)
        self.xml.write(out_path + self.filename + ".xml", pretty_print=pretty)

    def write_clean_csv(self, out_path="./"):

        header_rows = self.xml.xpath("/file/table/row[@role='header']")
        if len(header_rows):
            if len(header_rows) == 1:
                header = [x.text for x in header_rows[0].xpath(f"./cell[@role='header']/value")]
            else:
                header = []
                n_columns = max([len(row.xpath("cell")) for row in header_rows])
                for idx in range(n_columns):
                    header_i = []
                    for j in range(len(header_rows)):
                        hcell_val = header_rows[j].xpath(f"cell[position()={idx + 1}]/value")
                        if len(hcell_val):
                            header_i.append(hcell_val[0].text or "")
                    header.append((" ".join(header_i)))

            rows = [header]
        else:
            rows = []
        data_rows = self.xml.xpath("/file/table/row[@role='data']")
        if len(data_rows):
            for d in data_rows:
                cell_values = ["".join([v.text or "" for v in c if v.tag=="value"])for c in d.xpath("cell")]
                rows.append(cell_values)

        with open(out_path + self.filename, "w", encoding="utf8") as out:
            writer = csv.writer(out, delimiter=",", dialect="unix")
            writer.writerows(rows)

    def write_parameters(self, out_path="./"):
        encoding = self.xml.xpath("/file")[0].attrib["encoding"]
        lst_dels = [x.text for x in self.xml.xpath("//field_delimiter")]
        lst_quote = [x.text for x in self.xml.xpath("//quotation_char")]
        lst_rec = [x.text for x in self.xml.xpath("//record_delimiter")]
        lst_esc = [x.text for x in self.xml.xpath("//escape_char")]
        try:
            field_delimiter = max(set(lst_dels), key=lst_dels.count)
        except ValueError:
            field_delimiter = ""
        try:
            quotation_char = max(set(lst_quote), key=lst_quote.count)
        except ValueError:
            quotation_char = ""
        try:
            record_delimiter = max(set(lst_rec), key=lst_rec.count)
        except ValueError:
            record_delimiter = ""
        try:
            escape_char = max(set(lst_esc), key=lst_esc.count)
        except ValueError:
            escape_char = ""

        n_header_lines = len(self.xml.xpath(f"/file/table/row[@role='header']"))
        n_preamble_lines = len(self.xml.xpath(f"/file/table/row[@role='preamble']"))
        n_footnote_lines = len(self.xml.xpath(f"/file/table/row[@role='footnote']"))

        if self.xml.xpath(f"//*[@role='data']/.."):
            n_columns = max([len(row.xpath("cell")) for row in self.xml.xpath(f"/file/table/row[@role='data']")])
        else:
            n_columns = 0
        column_names = []
        if n_header_lines == 1:
            column_names = [x.text for x in self.xml.xpath(f"/file/table/row[@role='header']/cell/value")]
        elif n_header_lines > 1:
            # for every Nth children of a header row, get the value
            for idx in range(n_columns):
                header_i = " ".join([x.text for x in self.xml.xpath(f"/file/table/row[@role='header']/cell[position()={idx + 1}]/value")])
                column_names += [header_i]

        parameters_dict = {
            "encoding": encoding,
            "delimiter": field_delimiter,
            "quotechar": quotation_char,
            "escapechar": escape_char,
            "row_delimiter": record_delimiter,
            "header_lines": n_header_lines,
            "preamble_lines": n_preamble_lines,
            "footnote_lines": n_footnote_lines,
            "column_names": column_names,
            "n_columns": n_columns,
        }

        Path(out_path).mkdir(parents=True, exist_ok=True)
        with open(f"{out_path + self.filename}_parameters.json", "w") as out_file:
            json.dump(parameters_dict, out_file, indent=4)

    def __getstate__(self):
        state = self.__dict__.copy()
        state['xml'] = etree.tostring(state['xml'].getroot())
        return state


    def __setstate__(self, state):
        self.__dict__.update(state)
        self.xml = etree.ElementTree(etree.fromstring(state['xml']))

