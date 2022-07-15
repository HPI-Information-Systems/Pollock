FROM python:3.10.5-slim

WORKDIR /app
COPY ./sut/clevercs/clevercs.py ./
COPY ./sut/clevercs/clevercs-requirements.txt ./
COPY ./sut/utils.py ./

RUN pip install --no-cache-dir -r clevercs-requirements.txt
CMD ["python3", "clevercs.py"]