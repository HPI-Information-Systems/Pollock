FROM openjdk:11

WORKDIR /app
COPY ./sut/csvcommons/JCSV.java ./
COPY ./sut/csvcommons/commons-csv-1.9.0.jar ./
COPY ./sut/csvcommons/run-java.sh ./run-java.sh

RUN chmod +x run-java.sh
CMD /bin/bash ./run-java.sh