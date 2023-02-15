#!/bin/bash
rm -f JCSV.class
javac -cp ./opencsv-5.6.jar:./commons-lang3-3.12.0.jar:./json-20220924.jar JCSV.java
java -Xint -cp .:./opencsv-5.6.jar:./commons-lang3-3.12.0.jar:./json-20220924.jar JCSV