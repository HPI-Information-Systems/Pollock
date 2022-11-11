FROM python:3.10.5-slim

WORKDIR /app
COPY ./sut/pandas/panda.py ./
COPY ./sut/pandas/pandas-requirements.txt ./
COPY ./sut/utils.py ./

RUN pip install --no-cache-dir -r pandas-requirements.txt

CMD ["python3", "panda.py"]