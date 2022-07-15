FROM ubuntu:18.04
RUN apt-get update -y
RUN apt-get install -y python3 python3-dev build-essential wget

RUN wget https://www.sqlite.org/2022/sqlite-autoconf-3390000.tar.gz
RUN tar xvfz sqlite-autoconf-3390000.tar.gz
WORKDIR sqlite-autoconf-3390000/
RUN ./configure --prefix=/usr/local
RUN make
RUN make install

WORKDIR /app
COPY ./sut/sqlite/sqlite.py ./
COPY ./sut/utils.py ./

CMD ["python3", "sqlite.py"]
