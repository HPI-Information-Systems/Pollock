FROM ubuntu:18.04

WORKDIR /app
COPY ./sut/libreoffice/libreoffice.sh ./

RUN apt-get update -y
RUN apt-get install -y libreoffice

CMD ["bash", "libreoffice.sh"]
