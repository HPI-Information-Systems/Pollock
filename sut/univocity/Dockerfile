FROM openjdk:11

WORKDIR /app
COPY ./sut/univocity/JCSV.java ./
COPY ./sut/univocity/univocity-parsers-2.9.1.jar ./
COPY ./sut/univocity/run-java.sh ./run-java.sh

RUN chmod +x run-java.sh
CMD ./run-java.sh