#!/bin/bash
rm -f JCSV.class
javac -cp ./univocity-parsers-2.9.1.jar JCSV.java
java -cp .:./univocity-parsers-2.9.1.jar JCSV