FROM python:3.10.5-slim

WORKDIR /app
COPY ./sut/pycsv/pycsv.py ./

RUN pip install pandas==1.4.3
CMD ["python3", "pycsv.py"]
