import com.opencsv.CSVReader;
import com.opencsv.CSVWriter;

import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Objects;

public class JCSV {

    public static final String IN_DIR = "./results/polluted_files_csv/";
    public static final String OUT_DIR = "./results/loading/opencsv/";


    public static void processFile(File file, int i, int total) throws IOException {
        System.out.println("Processing file (" + i + "/" + total + ") " + file.getName());

        File outFile = new File(OUT_DIR + file.getName() + "_converted.csv");

        try {

            FileReader fileReader = new FileReader(file);
            CSVReader csvReader = new CSVReader(fileReader);

            FileWriter fileWriter = new FileWriter(outFile);
            CSVWriter csvWriter = new CSVWriter(fileWriter);


            String[] nextLine;
            while ((nextLine = csvReader.readNext()) != null) {
                csvWriter.writeNext(nextLine);
            }
            csvWriter.flush();
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

