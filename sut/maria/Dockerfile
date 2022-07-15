#FROM mariadb
#ENV MYSQL_USER=benchmark
#ENV MYSQL_PASSWORD=benchmark
#ENV MYSQL_ROOT_PASSWORD=benchmark
#ENV MYSQL_DATABASE=benchmark
#ENV MYSQL_TCP_PORT=3307
#ENV MYSQL_UNIX_PORT=3307

FROM python:3.10.5-slim

WORKDIR /app
COPY ./sut/maria/mariad.py ./
COPY ./sut/maria/mariadb-requirements.txt ./
COPY ./sut/utils.py ./

RUN  apt-get update \
  && apt-get install -y wget curl software-properties-common python3-pip\
  && rm -rf /var/lib/apt/lists/*
RUN wget https://downloads.mariadb.com/MariaDB/mariadb_repo_setup
RUN echo "d4e4635eeb79b0e96483bd70703209c63da55a236eadd7397f769ee434d92ca8  mariadb_repo_setup" | sha256sum -c
RUN chmod +x mariadb_repo_setup
RUN ./mariadb_repo_setup
RUN apt-get -y install libmariadb3 libmariadb-dev libmariadbclient-dev
RUN pip install mariadb

CMD ["python3", "mariad.py"]
