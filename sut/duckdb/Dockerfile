FROM python:3.10.5-slim

WORKDIR /app
COPY ./sut/duckdb/duck-bench.py ./
COPY ./sut/duckdb/duckdb-requirements.txt ./
COPY ./sut/utils.py ./

RUN apt-get update && apt-get install -y build-essential git cmake

RUN pip install --no-cache-dir -r duckdb-requirements.txt

# Clone the duckdb repository and build it
RUN git clone https://github.com/pdet/duckdb.git && \
    cd duckdb && \
    git checkout feature && \
    cd tools/pythonpkg  && \
    python3 setup.py install && \
    cd ../../..

CMD ["python3", "duck-bench.py"]

