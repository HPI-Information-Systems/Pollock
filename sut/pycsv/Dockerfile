FROM python:3.10.5-slim

WORKDIR /app
COPY ./sut/pycsv/pycsv.py ./
COPY ./sut/utils.py ./

CMD ["python3", "pycsv.py"]
