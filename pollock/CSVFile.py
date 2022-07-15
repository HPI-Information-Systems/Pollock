import pdb
import sys
import os
import csv
from pathlib import Path

import chardet
from clevercsv.dialect import SimpleDialect
from lxml import etree
from lxml.builder import E
import pandas as pd
from clevercsv.cparser_util import parse_string

# CSV_XSL = '''<xsl:stylesheet version="3.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"> <xsl:output method="text" />
# <xsl:template match="/">
#     <xsl:for-each select="//row">
#         <xsl:for-each select="child::*">
#             <xsl:value-of select="."/>
#         </xsl:for-each>
#     </xsl:for-each>
# </xsl:template>
# </xsl:stylesheet>'''
from .data_types import parse_cell

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


def create_cell(file, text: str, should_quote=False, role:str=None, **kwargs):
    """This function is used to create a cell element to be inserted in a files' XML,
        respecting quotation and escape characters.
        Keyword arguments are used as attributes in the resulting element.
        should_quote is used in case in the original file the cell was quoted regardless
    """
    cell = etree.Element("cell", role=role, **kwargs)

    to_quote = (text or '').find(file.field_delimiter) > 0
    if to_quote or should_quote:
        # q = etree.SubElement(r, "quotation_char")
        q = etree.SubElement(cell, "quotation_char")
        q.text = file.quotation_char

    # c.text = cell
    values = text.split(file.quotation_char)
    for vdx, v in enumerate(values):
        if vdx == 0:
            value = etree.SubElement(cell, "value")
            value.text = v
        else:
            escape = etree.SubElement(cell, "escape_char")
            escape.text = file.escape_char
            value = etree.SubElement(cell, "value")
            value.text = file.quotation_char + v

    if to_quote or should_quote:
        q = etree.SubElement(cell, "quotation_char")
        q.text = file.quotation_char

    return cell

class CSVFile:
    """This class is used to load a CSV file and record it as an XML tree
    """

    def __init__(self, filename, autodetect=False, record_delimiter="\r\n", field_delimiter=",", quotation_char='"', escape_char='"',
                 quote_all=False):

        self.filename = filename.split("/")[-1]
        self.col_count = -1
        self.row_count = 0
        root = etree.Element("file", filename=self.filename)

        if os.stat(filename).st_size == 0:
            self.xml = etree.ElementTree(root)
            return

        with open(filename, 'rb') as rawdata:
            result = chardet.detect(rawdata.read(1024 * 1024))  # just read the first megabyte

        encoding = result["encoding"]
        root.attrib["encoding"] = encoding

        if autodetect:
            with open(filename, newline='', encoding=encoding) as csvfile:
                dialect = csv.Sniffer().sniff(csvfile.read())
                csvfile.seek(0)
                content = list(csv.reader(csvfile, dialect))
                self.field_delimiter = dialect.delimiter
                self.record_delimiter = dialect.lineterminator
                self.quotation_char = dialect.quotechar
                self.encoding = encoding
        else:
            with open(filename, newline='', encoding=encoding) as csvfile:
                # content = list(csv.reader(csvfile, delimiter=field_delimiter, quotechar=quotation_char))
                data = csvfile.read()
            self.field_delimiter = field_delimiter
            self.record_delimiter = record_delimiter
            self.quotation_char = quotation_char
            self.encoding = encoding
            self.escape_char = escape_char

        table = etree.SubElement(root, "table")
        self.xmlrows = []
        self.quote_all = quote_all

        dialect = SimpleDialect(self.field_delimiter, self.quotation_char, "")
        for idx,row in enumerate(parse_string(data, dialect, return_quoted=True)):
            r = etree.SubElement(table, "row")
            n_cells = len(row)
            for j, (cell, is_quoted) in enumerate(row):
                # if to_quote or quote_all:
                #     q = etree.SubElement(r, "quotation_char")
                #     q.text = self.quotation_char
                role = "data" if idx > 0 else "header"
                typ = parse_cell(cell)
                # c = etree.SubElement(r, "cell", role=role, type=typ)

                c = create_cell(self, text=cell, role=role, type=typ, should_quote=is_quoted)
                r.insert(len(r), c)

                if j < n_cells - 1:
                    delimiter = E.field_delimiter(self.field_delimiter)
                    r.insert(len(r),delimiter)

            self.xmlrows += [r]
            if len(row) > self.col_count:
                self.col_count = len(row)
            row_delimiter = E.record_delimiter(self.record_delimiter)
            r.insert(len(r),row_delimiter)

        self.xml = etree.ElementTree(root)
        self.row_count = idx + 1

    # def save(self, out_path = "./"):
    #     last = len(self.content) - 1
    #     with open(out_path + self.filename, "w") as out_file:
    #
    #         for row in self.content:
    #             for idx,cell in enumerate(row):
    #                 if idx > 0:
    #                     out_file.write(self.record_delimiter)
    #                 to_quote = cell.find(self.quotation_char)
    #                 if to_quote>0:
    #                     out_file.write(self.quotation_char)
    #                 out_file.write(cell)
    #                 if to_quote>0:
    #                     out_file.write(self.quotation_char)
    #             out_file.write(self.field_delimiter)
    #
    #         out_file.close()

    def write_csv(self, out_path="./", verbose=False):
        xslt = etree.XML(CSV_XSL)
        transform = etree.XSLT(xslt)
        output = transform(self.xml)

        if verbose: print("\n" + str(output))
        Path(out_path).mkdir(parents=True, exist_ok=True)
        with open(out_path + self.filename, "w", encoding=self.encoding) as out:
            out.write(str(output))

    def write_xml(self, out_path="./", pretty=False):
        Path(out_path).mkdir(parents=True, exist_ok=True)
        self.xml.write(out_path + self.filename + ".xml", pretty_print=pretty)
        # with open(filename, "w") as out_file:
        #     out_file.write("<file>")
        #     for row in self.content:
        #         out_file.write("<row>")
        #         for idx,cell in enumerate(row):
        #             if idx > 0:
        #                 out_file.write("<field_delimiter>,</field_delimiter>")
        #             to_quote = cell.find(self.quotation_char)
        #             if to_quote>0:
        #                 out_file.write("<quotation_mark>" + self.quotation_char + "</quotation_mark>")
        #             out_file.write(f"<cell>{cell}</cell>")
        #             if to_quote>0:
        #                 out_file.write("<quotation_mark>" + self.quotation_char + "</quotation_mark>")
        #         out_file.write("</row>")
        #         out_file.write(f"<record_delimiter>{self.field_delimiter}</record_delimiter>")
        #     out_file.write("</file>")
        #     out_file.close()
