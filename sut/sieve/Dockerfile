FROM python:3.11.15-slim

WORKDIR /app
COPY ./sut/sieve/sieve-bench.py ./
COPY ./sut/sieve/sieve ./sieve
COPY ./sut/sieve/sieve-requirements.txt ./
COPY ./sut/utils.py ./

# sieve itself needs only the standard library; pandas is for sut/utils.py (save_time_df)
RUN pip install --no-cache-dir -r sieve-requirements.txt
CMD ["python3", "sieve-bench.py"]
