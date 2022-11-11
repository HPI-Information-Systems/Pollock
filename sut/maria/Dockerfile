FROM python:3.10.5-slim

WORKDIR /app
COPY ./sut/maria/mariad.py ./
COPY ./sut/maria/mariadb-requirements.txt ./
COPY ./sut/utils.py ./

RUN  apt-get update \
  && apt-get install -y wget curl software-properties-common python3-pip\
  && rm -rf /var/lib/apt/lists/*
RUN wget https://downloads.mariadb.com/MariaDB/mariadb_repo_setup
RUN echo "733cf126b03f73050e242102592658913d10829a5bf056ab77e7f864b3f8de1f  mariadb_repo_setup" | sha256sum -c
RUN chmod +x mariadb_repo_setup
RUN ./mariadb_repo_setup
RUN apt-get -y install libmariadb3 libmariadb-dev libmariadbclient-dev
RUN pip install mariadb

CMD ["python3", "mariad.py"]
