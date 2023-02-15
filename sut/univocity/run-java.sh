#!/bin/bash
rm -f JCSV.class
javac -cp ./univocity-parsers-2.9.1.jar:./json-20220924.jar JCSV.java
java -Xint -cp .:./univocity-parsers-2.9.1.jar:./json-20220924.jar JCSV