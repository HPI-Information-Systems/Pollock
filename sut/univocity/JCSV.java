import com.univocity.parsers.common.*;
import com.univocity.parsers.common.processor.*;
import com.univocity.parsers.common.record.*;
import com.univocity.parsers.conversions.*;
import com.univocity.parsers.csv.*;

import java.io.*;
import java.math.*;
import java.util.*;
import java.util.Map.*;
import java.util.concurrent.*;

public class JCSV {

    public static final String IN_DIR = "./results/polluted_files_csv/";
    public static final String OUT_DIR = "./results/loading/univocity/";


    public static void processFile(File file, int i, int total) throws IOException {
        System.out.println("Processing file (" + i + "/" + total + ") " + file.getName());

        File outFile = new File(OUT_DIR + file.getName() + "_converted.csv");
        try {
            CsvWriter writer = new CsvWriter(outFile, new CsvWriterSettings());

            StringBuilder out = new StringBuilder();
            FileReader fileReader = new FileReader(file);
            CsvParser parser = new CsvParser(new CsvParserSettings());
            parser.beginParsing(fileReader);
            String[] row;
            while ((row = parser.parseNext()) != null) {
                writer.writeRow(row);
            }
            writer.flush();

//            List<String[]> parsedRows = parser.parseAll(fileReader);
//            for (String[] row : parsedRows){
//                System.out.println(row.toString());
//            }

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
                    processFile(p, i, total);
                } catch (IOException e) {
                    System.out.println("Fatal error occured on file " + p.getName() + "\n Could not write Output file");
                }
                i++;
            }
        }

    }


    public static void main(String... args) {
        processFiles();
    }

}