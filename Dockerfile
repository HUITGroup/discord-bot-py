FROM python:3.11.4

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get clean
RUN pip install --upgrade pip

COPY . /work
WORKDIR /work

RUN mkdir -p log
RUN pip install -r requirements.txt

CMD ["python", "src/main.py"]
