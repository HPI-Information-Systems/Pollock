FROM python:3.10.5-slim

WORKDIR /app
COPY ./sut/duckdb/duck-bench.py ./
COPY ./sut/duckdb/duckdb-requirements.txt ./
COPY ./sut/utils.py ./

RUN apt-get update && apt-get install -y build-essential

RUN pip install --no-cache-dir -r duckdb-requirements.txt

RUN pip install duckdb --pre

CMD ["python3", "duck-bench.py"]