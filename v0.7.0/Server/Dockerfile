FROM python:3.10-slim

WORKDIR /Server

ADD . /Server

RUN pip install --trusted-host pypi.python.org -r requirements.txt

EXPOSE 5000
EXPOSE 5001
EXPOSE 5002

CMD ["python", "main.py"]

