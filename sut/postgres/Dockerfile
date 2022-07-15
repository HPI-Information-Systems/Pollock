FROM python:3.10.5

WORKDIR /app
COPY ./sut/postgres/postgresql.py ./
COPY ./sut/postgres/postgres-requirements.txt ./
COPY ./sut/utils.py ./

RUN pip install --no-cache-dir -r postgres-requirements.txt

CMD ["python3", "postgresql.py"]
