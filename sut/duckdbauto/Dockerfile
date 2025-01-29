FROM python:3.10.5-slim

WORKDIR /app
COPY ./sut/duckdbauto/duck-bench.py ./
COPY ./sut/duckdbauto/duckdb-requirements.txt ./
COPY ./sut/utils.py ./

RUN pip install --no-cache-dir -r duckdb-requirements.txt

RUN pip install duckdb --pre

CMD ["python3", "duck-bench.py"]

