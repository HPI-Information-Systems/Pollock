from __future__ import print_function
import builtins as __builtin__
from datetime import datetime
import time
import os
from copy import deepcopy
import constants
from CSVFile import CSVFile
import polluters_stdlib as pl
import polluters_base as pb
import lxml.etree as etree

OUT_CSV_PATH = "./results/files/polluted_files_csv/"
OUT_XML_PATH = "./results/files/polluted_files_xml/"

# Uncomment to clean output directories before run
# os.system('cd '+OUT_CSV_PATH+ ' && rm *.csv')
# os.system('cd '+OUT_XML_PATH+ ' && rm *.xml')+

def print(*args, **kwargs):
    return __builtin__.print(f"\033[94m{datetime.fromtimestamp(time.time()+3600).strftime('%H:%M:%S')}:\033[0m", *args, **kwargs)


def execute_polluter(file : CSVFile, polluter, *args, **kwargs):
    t = deepcopy(file)
    print("Executing", polluter.__name__, "with arguments", args)
    polluter(t, *args, **kwargs)
    t.write_csv(OUT_CSV_PATH)
    t.write_xml(OUT_XML_PATH)


f = CSVFile("./files/source.csv", quote_all=True, autodetect=False)


#Returns the source file
execute_polluter(f,pl.dummyPolluter)

#File name polluters
execute_polluter(f,pl.changeFilename, "source")
execute_polluter(f,pl.changeFilename, "\u00A0")
execute_polluter(f,pl.changeFilename, "\u00A0.csv")
execute_polluter(f,pl.changeFilename, "$.csv")
execute_polluter(f,pl.changeFilename, ".csv")
execute_polluter(f,pl.changeFilename, "source.tsv")
execute_polluter(f,pl.changeFilename, "source.pdf")
execute_polluter(f,pl.changeFilename, "source.loremipsumdolor")

#File dimension polluters
execute_polluter(f,pl.changeDimension, 0)
execute_polluter(f,pl.changeDimension, 200)

# File Encoding polluters
execute_polluter(f, pl.changeEncoding, constants.Encoding.UTF_8)
execute_polluter(f, pl.changeEncoding, constants.Encoding.LATIN_1)
execute_polluter(f, pl.changeEncoding, constants.Encoding.UTF_16)

#Number of columns
execute_polluter(f, pl.changeNumberColumns, 1)
execute_polluter(f, pl.changeNumberColumns, 1024)
execute_polluter(f, pl.changeNumberColumns, 17000)

#Number of rows
execute_polluter(f, pl.changeNumberRows, 1)
execute_polluter(f, pl.changeNumberRows, 99, True) #remove the header
execute_polluter(f, pl.changeNumberRows, 70000)

#Preamble
execute_polluter(f,pl.addPreamble,3,True) #delimited
execute_polluter(f,pl.addPreamble,3,False) #not delimited
execute_polluter(f,pl.addPreamble,3,True, True) #delimited, with empty
execute_polluter(f,pl.addPreamble,3,False, True) #not delimited with empty

#Footnote
execute_polluter(f,pl.addFootnote,3,True) #delimited
execute_polluter(f,pl.addFootnote,3,False) #not delimited
execute_polluter(f,pl.addFootnote,3,True, True) #delimited, with empty
execute_polluter(f,pl.addFootnote,3,False, True) #not delimited with empty

#Record Delimiter
execute_polluter(f,pl.changeRecordDelimiter,"\n")
execute_polluter(f,pl.changeRecordDelimiter,"\r")

#Field Delimiter
execute_polluter(f,pl.changeFieldDelimiter,";")
execute_polluter(f,pl.changeFieldDelimiter,"|")
execute_polluter(f,pl.changeFieldDelimiter," ")
execute_polluter(f,pl.changeFieldDelimiter,"\t")
execute_polluter(f,pl.changeFieldDelimiter,"\t\t")
execute_polluter(f,pl.changeFieldDelimiter,":")
execute_polluter(f,pl.changeFieldDelimiter,", ") #comma space
execute_polluter(f,pl.changeFieldDelimiter,"\u005C\u0074") #literally '\t'

#Quotation Char
execute_polluter(f,pl.changeQuotationChar, "\u0022")
execute_polluter(f,pl.changeQuotationChar, "\u0027")
execute_polluter(f,pl.changeQuotationChar, "\u0022\u0020") #quote-space

#Row Level Number Fields
execute_polluter(f,pl.changeRowNumberFields, 1,0) #row 1, empty
execute_polluter(f,pl.changeRowNumberFields, 1,15) #row 1, 15 fields
execute_polluter(f,pl.changeRowNumberFields, 1,5) #row 1, 5 fields

execute_polluter(f,pl.changeRowNumberFields, 2,0) #row 2, empty
execute_polluter(f,pl.changeRowNumberFields, 2,15) #row 2, 15 fields
execute_polluter(f,pl.changeRowNumberFields, 2,5) #row 2, 5 fields

execute_polluter(f,pl.changeRowNumberFields, 50,0) #row 3, empty
execute_polluter(f,pl.changeRowNumberFields, 50,15) #row 3, 15 fields
execute_polluter(f,pl.changeRowNumberFields, 50,5) #row 3, 5 fields

execute_polluter(f,pl.changeRowNumberFields, -1,0) #row -1, empty
execute_polluter(f,pl.changeRowNumberFields, -1,15) #row -1, 15 fields
execute_polluter(f,pl.changeRowNumberFields, -1,5) #row -1, 5 fields

#Row Level Record Delimiter
execute_polluter(f,pl.changeRowRecordDelimiter, 1, "\n")
execute_polluter(f,pl.changeRowRecordDelimiter, 2, "\n")
execute_polluter(f,pl.changeRowRecordDelimiter, 50, "\n")
execute_polluter(f,pl.changeRowRecordDelimiter, -1, "\n")

#Row Level Field Delimiter
execute_polluter(f,pl.changeRowFieldDelimiter, 1, ";")
execute_polluter(f,pl.changeRowFieldDelimiter, 2, ";")
execute_polluter(f,pl.changeRowFieldDelimiter, 50, ";")
execute_polluter(f,pl.changeRowFieldDelimiter, -1, ";")

#Row Level Quotation Mark
execute_polluter(f,pl.changeRowQuotationMark, 1,  "\u0027")
execute_polluter(f,pl.changeRowQuotationMark, 2,  "\u0027")
execute_polluter(f,pl.changeRowQuotationMark, 50,  "\u0027")
execute_polluter(f,pl.changeRowQuotationMark, -1, "\u0027")

#Column level Change Header
execute_polluter(f,pl.changeColumnHeader, 1, "HEADER", 2) # 1 regular, on multiple rows
execute_polluter(f,pl.changeColumnHeader, 3, "HEADER", 2)
execute_polluter(f,pl.changeColumnHeader,-1, "HEADER", 2)
execute_polluter(f,pl.changeColumnHeader, 1, "") # 1 empty
execute_polluter(f,pl.changeColumnHeader, 3, "")
execute_polluter(f,pl.changeColumnHeader,-1, "")
execute_polluter(f,pl.changeColumnHeader, 1, "HEAD/%R")
execute_polluter(f,pl.changeColumnHeader, 3, "HEAD/%R")
execute_polluter(f,pl.changeColumnHeader,-1, "HEAD/%R")
execute_polluter(f,pl.changeColumnHeader, [1,2], "HEADER")
execute_polluter(f,pl.changeColumnHeader, 1, "HEADER" * int(1e5)) # 1 large
execute_polluter(f,pl.changeColumnHeader, 3, "HEADER" * int(1e5))
execute_polluter(f,pl.changeColumnHeader,-1, "HEADER" * int(1e5))

#Table level add multiple table
execute_polluter(f,pl.addTable,10,6,False)
execute_polluter(f,pl.addTable,10,12,False)
execute_polluter(f,pl.addTable,10,6,True)
execute_polluter(f,pl.addTable,10,12,True)

#Table level change escape char
execute_polluter(f,pl.changeEscapeCharacter, "\\")
execute_polluter(f,pl.changeEscapeCharacter, '""')

#Table level change row escape char
execute_polluter(f,pl.changeRowEscapeChar, 1, "\\")
execute_polluter(f,pl.changeRowEscapeChar, 2, '\\')
execute_polluter(f,pl.changeRowEscapeChar, 50, '\\')
execute_polluter(f,pl.changeRowEscapeChar, -1, '\\')

for i in list(range(1,6))+[8]:
    execute_polluter(f,pl.changeColumnFormat, i,2)
    execute_polluter(f,pl.changeColumnFormat, i,50)
    execute_polluter(f,pl.changeColumnFormat, i,-1)
    #
    execute_polluter(f,pl.changeColumnFormat, i,range(1,50))
    execute_polluter(f,pl.changeColumnFormat, i,range(30,80))
    execute_polluter(f,pl.changeColumnFormat, i,range(50,100))

execute_polluter(f,pl.changeDimension, 1500000000)
# execute_polluter(f, pl.changeNumberRows, 2000000000)
