FROM openjdk:11

WORKDIR /app
COPY ./sut/univocity/JCSV.java ./
COPY ./sut/univocity/commons-csv-1.9.0.jar ./
COPY ./sut/univocity/run-java.sh ./run-java.sh

RUN chmod +x run-java.sh
CMD ./run-java.sh
#CMD ["java","-cp .:./opencsv-5.6.jar","JCSV"]
#CMD ["java","-cp",".:./opencsv-5.6.jar", "JCSV"]
#CMD java JCSV -cp .:./opencsv-5.6.jar
#CMD ["java", "JCSV"]