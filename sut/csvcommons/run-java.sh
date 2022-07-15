#!/bin/bash
rm -f JCSV.class
javac -cp ./commons-csv-1.9.0.jar JCSV.java
java -cp .:./commons-csv-1.9.0.jar:./ JCSV