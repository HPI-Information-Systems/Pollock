#!/bin/bash
rm -f JCSV.class
javac -cp ./opencsv-5.6.jar:./commons-lang3-3.12.0.jar JCSV.java
java -cp .:./opencsv-5.6.jar:./commons-lang3-3.12.0.jar JCSV