import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.charset.Charset;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Objects;
import java.io.UnsupportedEncodingException;

import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVRecord;
import org.apache.commons.csv.CSVPrinter;
import org.json.JSONObject;

public class JCSV {
    public static final String dataset = System.getenv("DATASET");
    public static final String sut = "csvcommons";
    public static final String IN_DIR = "/"+dataset+"/csv/";
    public static final String PARAM_DIR = "/"+dataset+"/parameters/";
    public static final String OUT_DIR = "/results/"+sut+"/"+dataset+"/loading/";
    public static final String TIME_DIR = "/results/"+sut+"/"+dataset;

    public static String processFile(File file, int i, int total) throws IOException {

        System.out.println("Processing file (" + i + "/" + total + ") " + file.getName());
        JSONObject sut_params = null;
        try {
            FileReader paramReader = new FileReader(PARAM_DIR + file.getName() + "_parameters.json");
            int paramChar = paramReader.read();
            String paramStr = "";
            while (paramChar != -1) {
                paramStr = paramStr + (char) paramChar;
                paramChar = paramReader.read();
            }
            sut_params = new JSONObject(paramStr);
        } catch (Exception e) {
            System.out.println("Could not read parameter file for " + file.getName());
        }
        File outFile = new File(OUT_DIR + file.getName() + "_converted.csv");
        String fileTime = "\""+file.getName()+"\"";

        String delim = (String) sut_params.get("delimiter");
        if (delim.equals("")) {
            delim = ",";
        }

        String quo = (String) sut_params.get("quotechar");
        if (quo.equals("")) {
            quo = "\"";
        }
        char quote = quo.charAt(0);

        String esc = (String) sut_params.get("escapechar");
        if (esc.equals("")) {
            esc = "\"";
        }
        char escape = esc.charAt(0);
        if (escape==quote) {
            escape = '\u0000'; // null character
        }
        String rs = (String) sut_params.get("row_delimiter");

        String encoding = ((String) sut_params.get("encoding")).toUpperCase();
        if (encoding.equals("ASCII")){
            encoding = "US-ASCII";
        }
        Charset charset = Charset.forName(encoding);

        final CSVFormat fmt = CSVFormat.Builder.create()
                .setAllowDuplicateHeaderNames(true).setAllowMissingColumnNames(true)
                .setDelimiter(delim).setQuote(quote).setEscape(escape)
                .setRecordSeparator(rs).build();


        for (int j = 0; j < 3; j++) {
            FileReader fileReader = new FileReader(file, charset);
            FileWriter fileWriter = new FileWriter(outFile);
            CSVParser csvParser = new CSVParser(fileReader, fmt);
            CSVPrinter csvPrinter = new CSVPrinter(fileWriter, CSVFormat.DEFAULT);

            int n_rows = 0;
            double duration = 0;
            long startTime = System.nanoTime();
            try {
                Iterable<CSVRecord> rows = csvParser.getRecords();
                long endTime = System.nanoTime();
                duration = (endTime - startTime) / 1000000000F;
                for (CSVRecord record : rows) {
                    csvPrinter.printRecord(record.toList());
                    n_rows++;
                }
                csvPrinter.flush();
            } catch (Exception e) {
                long endTime = System.nanoTime();
                if (j==0) {
                    System.out.println("Error processing file " + file.getName());
                    System.out.println("\t"+e.getMessage());
                }
                n_rows = 0;
                duration = (endTime - startTime) / 1000000000F;
                FileWriter exceptionWriter = new FileWriter(outFile);
                exceptionWriter.write("Application Error\n" + e);
                exceptionWriter.close();
            }
            fileTime = fileTime + "," + String.valueOf(duration);
        }
        return fileTime.substring(0, fileTime.length());
    }

    public static void processFiles() {
        ArrayList<File> files = new ArrayList<>(List.of(Objects.requireNonNull(new File(IN_DIR).listFiles())));
        int total = files.size();
        int i = 1;
        List<String> timeResults = new ArrayList<>();
        for (File f : files) {
            String outFilePath = OUT_DIR + f.getName() + "_converted.csv";
            File outF = new File(outFilePath);
            if (!outF.exists()) {
                try {
                    String strTime = processFile(f, i, total);
                    timeResults.add(strTime);
                } catch (IOException e) {
                    System.out.println("Fatal error occurred on file " + f.getName() + "\n Could not write Output file");
                }
            }
            i++;
        }
        if (timeResults.size() == 0) {
            System.out.println("No files to process");
            return;
        }
        try {
            FileWriter timeWriter = new FileWriter(TIME_DIR + "/"+sut+"_time.csv");
            timeWriter.write("filename,"+sut+"_time_0,"+sut+"_time_1,"+sut+"_time_2\n");
            for (String time : timeResults) {
                timeWriter.write(time + "\n");
            }
            timeWriter.close();
        } catch (IOException e) {
            System.out.println("Could not write time file");
        }
    }


    public static void main(String... args) {
        processFiles();
    }

}

