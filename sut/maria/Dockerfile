FROM python:3.10.5-slim

WORKDIR /app
COPY ./sut/maria/mariad.py ./
COPY ./sut/maria/mariadb-requirements.txt ./
COPY ./sut/utils.py ./

RUN  apt-get update \
  && apt-get install -y wget curl software-properties-common python3-pip\
  && rm -rf /var/lib/apt/lists/*
RUN wget https://downloads.mariadb.com/MariaDB/mariadb_repo_setup
RUN chmod +x mariadb_repo_setup
RUN ./mariadb_repo_setup
RUN apt-get -y install libmariadb3 libmariadb-dev libmariadbclient-dev
RUN pip install mariadb pandas==1.4.3

CMD ["python3", "mariad.py"]
