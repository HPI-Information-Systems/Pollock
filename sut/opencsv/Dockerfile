FROM openjdk:11

WORKDIR /app
COPY ./sut/opencsv/JCSV.java ./
COPY ./sut/opencsv/opencsv-5.6.jar ./
COPY ./sut/opencsv/commons-lang3-3.12.0.jar ./
COPY ./sut/opencsv/run-java.sh ./run-java.sh

RUN chmod +x run-java.sh
CMD /bin/bash ./run-java.sh