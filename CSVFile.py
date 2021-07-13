import sys
import os
import csv

import chardet
from lxml import etree
import pandas as pd

from data_types import parse_cell

CSV_XSL = '''<xsl:stylesheet version="3.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"> <xsl:output method="text" /> 
<xsl:template match="/">
    <xsl:for-each select="//row">
        <xsl:for-each select="child::*">
            <xsl:value-of select="."/>
        </xsl:for-each>
    </xsl:for-each>
</xsl:template>
</xsl:stylesheet>'''


csv.field_size_limit(sys.maxsize)

def insert_value_cell(file, element, text:str):
    """This function is used to insert the content within a cell element in the XML,
        respecting quotation and escape characters
    """
    to_quote = (text or '').find(file.field_delimiter) > 0
    if to_quote or file.quote_all:
        q = etree.SubElement(element, "quotation_char")
        q.text = file.quotation_char

    values = text.split(file.quotation_char)
    for vdx, v in enumerate(values):
        if vdx == 0:
            value = etree.SubElement(element, "value")
            value.text = v
        else:
            escape = etree.SubElement(element, "escape_char")
            escape.text = file.escape_char
            value = etree.SubElement(element, "value")
            value.text = file.quotation_char + v

    if to_quote or file.quote_all:
        q = etree.SubElement(element, "quotation_char")
        q.text = file.quotation_char


class CSVFile:
    """This class is used to load a CSV file and record it as an XML tree
    """
    def __init__(self, filename, autodetect = False, record_delimiter ="\r\n", field_delimiter=",", quotation_char ='"', escape_char = '"', quote_all = False):

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
                content = list(csv.reader(csvfile, delimiter=field_delimiter, quotechar=quotation_char))
            self.field_delimiter = field_delimiter
            self.record_delimiter = record_delimiter
            self.quotation_char = quotation_char
            self.encoding = encoding
            self.escape_char = escape_char

        self.df = pd.DataFrame(content)

        table = etree.SubElement(root, "table")
        self.xmlrows = []
        self.quote_all = quote_all

        for idx,row in enumerate(content):
            r = etree.SubElement(table, "row")
            n_cells = len(row)
            for j,cell in enumerate(row):
                role = "data" if idx>0 else "header"
                typ = parse_cell(cell)
                c = etree.SubElement(r, "cell", role=role, type=typ)

                insert_value_cell(self,element=c,text=cell)

                if j < n_cells-1:
                    cd = etree.SubElement(r, "field_delimiter")
                    cd.text = self.field_delimiter
            self.xmlrows += [r]
            if len(row)>self.col_count:
                self.col_count = len(row)
            rd = etree.SubElement(r,"record_delimiter")
            rd.text = self.record_delimiter

        self.xml = etree.ElementTree(root)
        self.row_count = idx+1

    def write_csv(self, out_path = "./", verbose = False):
        xslt = etree.XML(CSV_XSL)
        transform = etree.XSLT(xslt)
        output = transform(self.xml)

        if verbose: print("\n" + str(output))
        with open(out_path + self.filename, "w", encoding= self.encoding) as out:
            out.write(str(output))

    def write_xml(self, out_path = "./", pretty=False):
        self.xml.write(out_path + self.filename+".xml", pretty_print=pretty)