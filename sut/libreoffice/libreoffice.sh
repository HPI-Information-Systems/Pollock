#!/bin/bash
#https://wiki.openoffice.org/wiki/Documentation/DevGuide/Spreadsheets/Filter_Options#Token_9.2C_csv_import
#infilter: 
#   field_delimiter as ASCII code (e.g. "," is 44) or FIX
#   quotation mark as ASCII code  (e.g. " is 34)
#   character set
#   first line to convert
#   cell format of columns (check webbpage for reference)
#   extra stuff not necessary
 
IN_DIR="./results/polluted_files_csv/"
OUT_DIR="/app/results/loading/libreoffice/"
TMP_DIR="/app/results/loading/libreoffice/xlsx/"

function to_xlsx(){
    filename="$1"
    local parameters="${2:-'44,34,ASCII'}"
    new="${f%.*}"
    {
    libreoffice --headless --convert-to xlsx:"Calc MS Excel 2007 XML" --infilter="$local_parameters" "$filename" --outdir "$TMP_DIR" && \
    mv "$TMP_DIR$new.xlsx" "$TMP_DIR${filename}_converted.xlsx"
    } || {
        echo "Application Error" > "$OUT_DIR${filename}_converted.csv"
    }
    echo ""
}

cd "$IN_DIR"


#for f in file_field_delimiter*
#do
#    tmp="${f%.csv*}"
#    tmp="${tmp#*file_field_delimiter_}"
#    IFS='_' read -r -a array <<< "$tmp"

#    delimiters=$(printf "/%d" "${array[@]}")
#    delimiters=${delimiters:1}
#    MRG="/MRG"

#    [[ "${#array[@]}" -gt "1" ]] && parameters={"$delimiters$MRG,34,ASCII"} || parameters={"$delimiters,34,ASCII"}

#    to_xlsx "$f" "$parameters"
#done

#for f in file_quotation_char*
#do
#    tmp="${f%.csv*}"
#    tmp="${tmp#*table_quotation_char_}"
#    IFS='_' read -r -a array <<< "$tmp"
#    quotations=$(printf "%d" "${array[0]}") #Libreoffice only has one quotation mark, so we take the first
#    parameters={"44,$quotations,ASCII"}
#    to_xlsx "$f" "$parameters"
#done

#for f in file_double_trailing* file_header* file_multitable* file_no* file_one* file_preamble* file_record* row_extra* row_less* row_more* file_escape_char*
for f in file_escape_char*
do
    to_xlsx "$f"
done

to_xlsx source.csv
#for f in row_field_delimiter_*
#do
#    tmp="${f%.csv*}"
#    tmp="${tmp#*0x}"
#    IFS='_' read -r -a array <<< "0x$tmp"
#    delimiters=$(printf "%d/" "${array[@]}")
#    delimiters=${delimiters::-1}
#    parameters={"$delimiters,34,ASCII"}
#    to_xlsx "$f" "$parameters"
#done

for file in "$TMP_DIR"*.xlsx
do
    echo "Converting $file"
    libreoffice --headless --convert-to csv:"Text - txt - csv (StarCalc)" "$file" --outdir "$OUT_DIR"
    echo ""
done
