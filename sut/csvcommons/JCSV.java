import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Objects;
import java.io.UnsupportedEncodingException;

import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVRecord;
import org.apache.commons.csv.CSVPrinter;

public class JCSV {

    public static final String IN_DIR = "./results/polluted_files_csv/";
    public static final String OUT_DIR = "./results/loading/csvcommons/";

    public static String parse_utf(String str, String rplc) {
        String utf = str.replaceAll(rplc, "");
        utf = utf.replaceAll(".csv", "");
        String arr[] = utf.replaceAll("0x", "").trim().split("_");
        byte[] utf8 = new byte[arr.length];
        int index = 0;
        for (String ch : arr) {
            utf8[index++] = (byte) Integer.parseInt(ch, 16);
        }
        try {
            String out = new String(utf8, "UTF-8");
            return out;
        } catch (UnsupportedEncodingException e) {
            return "";
            // handle the UTF-8 conversion exception
        }
    }

    public static void processFile(File file, int i, int total) throws IOException {
        System.out.println("Processing file (" + i + "/" + total + ") " + file.getName());

        File outFile = new File(OUT_DIR + file.getName() + "_converted.csv");
        try {

            FileReader fileReader = new FileReader(file);
            FileWriter fileWriter = new FileWriter(outFile);
            String delim = new String(",");
            String esc = new String("\"");
            char quote = '"';
            String rs = new String("\r\n");

            String in_filepath = file.getName();
            if (in_filepath.contains("file_field_delimiter_")) {
                delim = parse_utf(in_filepath, "file_field_delimiter_");
            }

            if (in_filepath.contains("file_quotation_char_")) {
                String str_quote = parse_utf(in_filepath, "file_quotation_char_");
                quote = str_quote.charAt(0);
                esc = Character.toString(quote);
            }

            if (in_filepath.contains("file_record_delimiter_")) {
                rs = parse_utf(in_filepath, "file_record_delimiter_");
            }

            final CSVFormat fmt = CSVFormat.Builder.create()
                    .setDelimiter(delim).setQuote(quote).setRecordSeparator(rs).build();

            CSVParser csvParser = new CSVParser(fileReader, fmt);
            CSVPrinter csvPrinter = new CSVPrinter(fileWriter, CSVFormat.DEFAULT);

            for (CSVRecord record : csvParser) {
                csvPrinter.printRecord(record.toList());
            }
            csvPrinter.flush();

        } catch (Exception e) {
            System.out.println("Application error on file " + file.getName());
            System.out.println(e);
            FileWriter exceptionWriter = new FileWriter(outFile);
            exceptionWriter.write("Application Error\n" + e);
            exceptionWriter.close();
        }
    }

    public static void processFiles() {
        ArrayList<File> files = new ArrayList<>(List.of(Objects.requireNonNull(new File(IN_DIR).listFiles())));
        int total = files.size();
        int i = 1;
        for (File p : files) {
            String outFilePath = OUT_DIR + p.getName() + "_converted.csv";
            File outF = new File(outFilePath);
            if (!outF.exists()) {
                try {
                    System.out.println(String.valueOf(i) + " " + p.getName());
                    processFile(p, i, total);
                } catch (IOException e) {
                    System.out.println("Fatal error occured on file " + p.getName() + "\n Could not write Output file");
                }
            }
            i++;
        }

    }


    public static void main(String... args) {
        processFiles();
    }

}

