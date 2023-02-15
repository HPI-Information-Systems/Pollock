import com.univocity.parsers.common.*;
import com.univocity.parsers.common.processor.*;
import com.univocity.parsers.common.record.*;
import com.univocity.parsers.conversions.*;
import com.univocity.parsers.csv.*;

import java.io.*;
import java.math.*;
import java.nio.charset.Charset;
import java.util.*;
import java.util.Map.*;
import java.util.concurrent.*;
import org.json.JSONObject;

public class JCSV {
    public static final String dataset = System.getenv("DATASET");
    public static final String sut = "univocity";
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
        String fileTime = "\""+file.getName() + "\"";

        String encoding = ((String) sut_params.get("encoding")).toUpperCase();
        if (encoding.equals("ASCII")){
            encoding = "US-ASCII";
        }
        Charset charset = Charset.forName(encoding);

        for (int j = 0; j < 3; j++) {
            int n_rows = 0;
            double duration = 0;
            long startTime = System.nanoTime();

            try {
                CsvWriter writer = new CsvWriter(outFile, new CsvWriterSettings());
                FileReader fileReader = new FileReader(file,charset);
                CsvParser parser = new CsvParser(new CsvParserSettings());
                List<String[]> parsedRows = parser.parseAll(fileReader);
                long endTime = System.nanoTime();
                duration = (endTime - startTime)/ 1000000000F;
                for (String[] row : parsedRows) {
                    writer.writeRow(row);
                }
                writer.flush();
            } catch (Exception e) {
                long endTime = System.nanoTime();
                duration = (endTime - startTime)/ 1000000000F;
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
        for (File p : files) {
            String outFilePath = OUT_DIR + p.getName() + "_converted.csv";
            File outF = new File(outFilePath);
             if (!outF.exists()) {
                System.out.println("Processing file "+outFilePath);
                try {
                    String strTime = processFile(p, i, total);
                    timeResults.add(strTime);
                } catch (IOException e) {
                    System.out.println("Fatal error occurred on file " + p.getName() + "\n Could not write Output file");
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
            System.out.println("Fatal error occurred could not write time file");
        }

    }


    public static void main(String... args) {
        processFiles();
    }

}
