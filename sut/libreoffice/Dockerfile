FROM ubuntu:22.04

WORKDIR /app
COPY ./sut/libreoffice/libreoffice.py ./
COPY ./sut/utils.py ./

RUN apt-get update -y
RUN apt-get install -y libreoffice=1:7.3.7-0ubuntu0.22.04.1 python3-pip
RUN pip install pandas==1.4.3

CMD ["python3", "libreoffice.py"]