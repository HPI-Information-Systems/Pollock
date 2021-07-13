import random
import string
import time

import constants
import polluters_base as pb
from CSVFile import CSVFile, insert_value_cell
from lxml import etree



def dummyPolluter(file:CSVFile):
    pass

def changeFilename(file: CSVFile, target_name):
    file.filename = target_name
    file.xml.getroot().attrib["filename"] = target_name


def changeDimension(file: CSVFile, target_dimension=-1):
    """
        param target_dimension: number of bytes tp reach, -1 to leave it intact
    """
    content = []
    for i in range(file.row_count):
        content += ["".join([x for x in file.xml.xpath(f"//row[{i+1}]//node()[not(node())]")])]
    textcontent = "".join(content)
    cur_size = len(textcontent)

    last_row_cells = [x for x in file.xml.xpath("//row[last()]//cell")]
    last_row_content = ["".join(v.text) for c in last_row_cells for v in c if v.tag=="value"]

    size_last_row = len("".join(content[-1]))
    n_rows = int((target_dimension - cur_size) / size_last_row)

    if target_dimension > cur_size:
        pb.addRows(file, cell_content=last_row_content, n_rows=n_rows, position=-1, role="data")
    elif 0 <= target_dimension < cur_size:
        n_rows_to_keep = textcontent.count("\r\n", target_dimension)
        if target_dimension:
            n_rows_to_keep -= 1  # exclude the current if dimension breaks one in half (if not exactly 0)
        remove_rows = list(range(file.row_count - n_rows_to_keep, file.row_count + 1))
        pb.deleteRows(file, rows_to_delete=remove_rows)

    file.filename = "file_dimension_" + str(target_dimension) + ".csv"
    file.xml.getroot().attrib["filename"] = file.filename

    return


def changeEncoding(file: CSVFile, target_encoding: constants.Encoding):
    target = target_encoding.value if type(target_encoding) == constants.Encoding else target_encoding
    assert (target in constants.Encoding.supported_encodings.value)

    file.encoding = target
    file.filename = "file_encoding_" + target + ".csv"
    file.xml.getroot().attrib["filename"] = file.filename
    file.xml.getroot().attrib["encoding"] = target


def changeNumberColumns(file: CSVFile, target_number_cols: int):
    if target_number_cols < file.col_count:
        cols_delete = list(range(target_number_cols, file.col_count))
        pb.deleteColumns(file, col=cols_delete)

    if target_number_cols > file.col_count:
        rn = range(file.col_count, target_number_cols)
        t = time.time()
        roles = ["header"]+["data"]*(file.row_count-1)
        content = []

        for i in range(file.row_count):
            content += ["".join([val.text for val in file.xml.xpath(f"//row[{i + 2}]/cell[last()]/value")]) ] #xpath is 1-indexed plus row 1 is header
        pb.addColumns(file, -1, col_names=["col" + str(i + 1) for i in rn], n_cols=len(rn), cell_content=content, role=roles)
        print("took", time.time() - t, "seconds")

    file.filename = "table_num_columns_" + str(target_number_cols) + ".csv"
    file.xml.getroot().attrib["filename"] = file.filename
    return


def changeNumberRows(file: CSVFile, target_number_rows: int, remove_header=False):

    last_row_cells = [x for x in file.xml.xpath("//row[last()]//cell")]
    last_row_content = ["".join(v.text) for c in last_row_cells for v in c if v.tag=="value"]

    if remove_header:
        pb.deleteRows(file, [0])

    if target_number_rows < file.row_count:
        rows_delete = list(range(target_number_rows, file.row_count))
        pb.deleteRows(file, rows_to_delete=rows_delete)

    if target_number_rows > file.row_count:
        n_rows = target_number_rows - file.row_count
        t = time.time()
        pb.addRows(file, cell_content=last_row_content, n_rows=n_rows, position=-1, role="data")
        print("took", time.time() - t, "seconds")

    file.filename = f"table_num_rows_{str(target_number_rows)}{'_no_header' if remove_header else ''}.csv"
    file.xml.getroot().attrib["filename"] = file.filename
    return


def addPreamble(file: CSVFile, n_rows=1, delimiters=False, emptyrow=False, cell_content="PREAMBLE"):
    """
    :param file:
    :param n_rows: number of rows for the preamble
    :param delimiters: if True, creates a row with as many delimited cells as the other rows
    :param emptyrow:  if True, leaves an empty row between the preamble and the data
    :param cell_content: the content of the preamble cell(s). Either list or single value
    """
    if emptyrow:
        pb.addRows(file, n_rows=1, position=0, col_count=file.col_count, role="metadata")

    if delimiters:
        cell_content = [cell_content] + [''] * (file.col_count - 1) if type(cell_content) == str else cell_content
        pb.addRows(file, n_rows=n_rows, cell_content=cell_content, position=0, col_count=file.col_count, role="metadata")

    else:
        pb.addRows(file, n_rows=n_rows, cell_content=cell_content, position=0, col_count=1, role="metadata")

    file.filename = f"table_preamble_{n_rows}_{'not_' if not delimiters else ''}delimited{'_empty_row' if emptyrow else ''}.csv"
    file.xml.getroot().attrib["filename"] = file.filename
    return


def addFootnote(file: CSVFile, n_rows=1, delimiters=False, emptyrow=False, cell_content="FOOTNOTE"):
    """
    :param file:
    :param n_rows: number of rows for the preamble
    :param delimiters: if True, creates a row with as many delimited cells as the other rows
    :param emptyrow:  if True, leaves an empty row between the preamble and the data
    :param cell_content: the content of the preamble cell(s). Either list or single value
    """
    if emptyrow:
        pb.addRows(file, n_rows=1, position=-1, col_count=file.col_count, role="metadata")

    if delimiters:
        cell_content = [cell_content] + [''] * (file.col_count - 1) if type(cell_content) == str else cell_content
        pb.addRows(file, n_rows=n_rows, cell_content=cell_content, position=-1, col_count=file.col_count, role="metadata")

    else:
        pb.addRows(file, n_rows=n_rows, cell_content=cell_content, position=-1, col_count=1, role="metadata")

    file.filename = f"table_footnote_{n_rows}_{'not_' if not delimiters else ''}delimited{'_empty_row' if emptyrow else ''}.csv"
    file.xml.getroot().attrib["filename"] = file.filename
    return


def changeRecordDelimiter(file: CSVFile, target_delimiter="\r\n"):
    file.record_delimiter = target_delimiter
    root = file.xml.getroot()
    query = root.xpath(f"//record_delimiter")
    for r in query:
        r.text = target_delimiter

    vals = [ord(x) for x in target_delimiter]
    del_string = ''.join([f'_0x{v:X}' for v in vals])
    file.filename = f"table_record_delimiter{del_string}.csv"
    file.xml.getroot().attrib["filename"] = file.filename


def changeFieldDelimiter(file: CSVFile, target_delimiter=";", fixed_width=False):
    file.field_delimiter = target_delimiter
    root = file.xml.getroot()
    query = root.xpath(f"//field_delimiter")
    for fd in query:
        fd.text = target_delimiter

    vals = [ord(x) for x in target_delimiter]
    del_string = ''.join([f'_0x{v:X}' for v in vals])
    file.filename = f"table_field_delimiter{del_string}.csv"
    file.xml.getroot().attrib["filename"] = file.filename

def changeEscapeCharacter(file: CSVFile, target_escape="\\"):
    file.escape_char = target_escape
    root = file.xml.getroot()
    query = root.xpath(f"//escape_char")
    for e in query:
        e.text = target_escape

    vals = [ord(x) for x in target_escape]
    e_string = ''.join([f'_0x{v:X}' for v in vals])
    file.filename = f"table_escape_char{e_string}.csv"
    file.xml.getroot().attrib["filename"] = file.filename



def changeQuotationChar(file: CSVFile, target_char="\u0022"):
    file.quotation_char = target_char
    root = file.xml.getroot()
    query = root.xpath(f"//quotation_char")
    for idx,qc in enumerate(query):
        if not idx%2:
            qc.text = target_char
        else:
            qc.text = target_char[::-1] #reverse it for multi-line

    vals = [ord(x) for x in target_char]
    quote_string = ''.join([f'_0x{v:X}' for v in vals])
    file.filename = f"table_quotation_char{quote_string}.csv"
    file.xml.getroot().attrib["filename"] = file.filename


def changeRowNumberFields(file: CSVFile, row=1, target_n_cells=1):
    if type(row) == int and row < 0:
        row = "last()-" + str(row + 1)

    if target_n_cells == -1 or target_n_cells == file.col_count:
        strtype = "homogeneous"
    if target_n_cells == 0:
        strtype = "empty"
        pb.deleteCells(file, row=row, col=list(range(target_n_cells, file.col_count)))
    elif target_n_cells < file.col_count:
        strtype = "less"
        pb.deleteCells(file, row=row, col=list(range(target_n_cells, file.col_count)))
    elif target_n_cells > file.col_count:
        strtype = "more"
        root = file.xml.getroot()
        content = "".join([v.text for v in root.xpath(f"//row[{row}]/cell[last()]")[0] if v.tag == "value"])
        pb.addCells(file, row=row, position=-1, content=content, n_cells=target_n_cells - file.col_count)

    file.filename = f"row_n_fields_{row}_{strtype}.csv"
    file.xml.getroot().attrib["filename"] = file.filename


def changeRowRecordDelimiter(file: CSVFile, row=1, target_delimiter="\r\n"):
    if type(row) == int and row < 0:
        row = "last()-" + str(row + 1)

    root = file.xml.getroot()
    root.xpath(f"//row[{row}]/record_delimiter")[0].text = target_delimiter

    vals = [ord(x) for x in target_delimiter]
    del_string = ''.join([f'_0x{v:X}' for v in vals])
    file.filename = f"row_record_delimiter_{row}{del_string}.csv"
    file.xml.getroot().attrib["filename"] = file.filename


def changeRowFieldDelimiter(file: CSVFile, row=1, target_delimiter=";"):
    """
        Row indexing is 1-based - following xquery
    """
    if type(row) == int and row < 0:
        row = "last()-" + str(row + 1)

    root = file.xml.getroot()
    query = root.xpath(f"//row[{row}]/field_delimiter")
    for r in query:
        r.text = target_delimiter

    vals = [ord(x) for x in target_delimiter]
    del_string = ''.join([f'_0x{v:X}' for v in vals])
    file.filename = f"row_field_delimiter_{row}{del_string}.csv"
    file.xml.getroot().attrib["filename"] = file.filename


def changeRowQuotationMark(file: CSVFile, row=1, target_quotation="'"):
    """
        Row indexing is 1-based - following xquery
    """
    if type(row) == int and row < 0:
        row = "last()-" + str(row + 1)

    root = file.xml.getroot()
    query = root.xpath(f"//row[{row}]//quotation_char")
    for r in query:
        r.text = target_quotation

    vals = [ord(x) for x in target_quotation]
    quote_string = ''.join([f'_0x{v:X}' for v in vals])
    file.filename = f"row_quotation_mark_{row}{quote_string}.csv"
    file.xml.getroot().attrib["filename"] = file.filename


def changeRowEscapeChar(file: CSVFile, row=1, target_escape="\\"):
    """
        If the row content does not include an escape character, add it anyway to every cell
    """
    if type(row) == int and row < 0:
        row = "last()-" + str(row + 1)

    root = file.xml.getroot()
    for cell in root.xpath(f"//row[{row}]/cell"):
        content = "".join([v.text for v in cell if v.tag=="value"])
        content += file.quotation_char
        [cell.remove(child) for child in cell]
        insert_value_cell(file,cell,content)

    query = root.xpath(f"//row[{row}]//escape_char")
    for r in query:
        r.text = target_escape

    vals = [ord(x) for x in target_escape]
    esc_string = ''.join([f'_0x{v:X}' for v in vals])
    file.filename = f"row_escape_char_{row}{esc_string}.csv"
    file.xml.getroot().attrib["filename"] = file.filename


def changeColumnHeader(file: CSVFile, col: int, target_header="HEADER", extra_rows=0):
    """
        If >0, extra rows expands the header on X many rows
    """
    colint = col
    if type(col) == int and col < 0:
        col = "last()-" + str(col + 1)

    if type(col) == list:
        [pb.changeCell(file, row=1, col=c, new_content=target_header) for c in col]
    else:
        pb.changeCell(file, row=1, col=col, new_content=target_header)

    if extra_rows > 0:
        if type(target_header) == str:
            cell_content = [''] * (file.col_count)
            if type(col) == list:
                for c in cell_content:
                    cell_content[c] = target_header
            else:
                cell_content[colint] = target_header
        else:
            cell_content = target_header
        pb.addRows(file, n_rows=extra_rows, cell_content=cell_content, position=0, col_count=file.col_count)

    if len(target_header) in range(1, 255):
        strtype = "regular"
    elif not len(target_header):
        strtype = "empty"
    else:
        strtype = "large"
    if not target_header.isalnum():
        strtype+="_nonalnum"


    file.filename = f"column_header_{col}_{strtype}{'_multiple' if extra_rows > 0 else ''}{'_nonunique' if type(col)==list else ''}.csv"
    file.xml.getroot().attrib["filename"] = file.filename


def addTable(file: CSVFile, n_rows, n_cols, empty_boundary=True):
    """Adds a table after the first one with n_rows and n_cols.
       Additionally, can be specified if the two are separated by empty delimited rows or not.
    """

    random.seed(constants.RAND_SEED)
    root = file.xml.getroot()
    old_table = root.xpath("//table")[0]
    new_table = etree.SubElement(root, "table")

    content = []
    for i in range(n_rows):
        content += [[x.text for x in old_table.xpath(f"//row[{i+1}]//value")]]

    for i in range(n_rows):
        row_cells = content[i]
        pb.addRows(file, cell_content=row_cells, n_rows=1, position=-1, table=1)

    if n_cols == file.col_count:
        strtype = "same"
    elif n_cols < file.col_count:
        strtype = "less"
        cols_delete = list(range(n_cols, file.col_count))
        pb.deleteColumns(file, col=cols_delete, table=1)
    elif n_cols > file.col_count:
        strtype = "more"
        cols_add = len(range(file.col_count, n_cols))
        col_names=["col" + str(i + 1) for i in range(cols_add)]
        content = []
        for i in range(1,n_rows):
            content += [file.xml.xpath(f"//table[1]//row[{i + 1}]/cell[last()]/value")[0].text]

        pb.addColumns(file, position=-1, n_cols=cols_add, col_names = col_names, cell_content = content, table=1)

    if empty_boundary:
        pb.addRows(file, cell_content="", n_rows=1, position=0, table=1)

    file.filename = f"table_multitable_rows_{n_rows}_{strtype}_cols{'_separated' if empty_boundary else ''}.csv"
    file.xml.getroot().attrib["filename"] = file.filename


def changeColumnFormat(file:CSVFile, col= 1, row=1):
    """Changes the syntactic values of a column, either in one cell or in multiple cells (expressable with an iterable)
    """
    root = file.xml.getroot()
    cells = []
    try:
        for r in row:
            pb.changeCellFormat(file, r, col)
    except TypeError:
        pb.changeCellFormat(file, row, col)

    file.filename = f"column_heterogeneous_format_col{col}_row_{row}.csv"
    file.xml.getroot().attrib["filename"] = file.filename
