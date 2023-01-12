FROM ubuntu:22.04

WORKDIR /app
COPY ./sut/libreoffice/libreoffice.py ./
COPY ./sut/utils.py ./

RUN apt-get update -y
RUN apt-get install -y libreoffice=1:7.3.7-0ubuntu0.22.04.1

CMD ["python3", "libreoffice.py"]