#!/bin/bash
rm -f JCSV.class
javac -cp ./commons-csv-1.9.0.jar:./json-20220924.jar JCSV.java
java -Xint -cp .:./commons-csv-1.9.0.jar:./json-20220924.jar:./ JCSV