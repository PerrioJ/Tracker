FROM python:latest

WORKDIR /Home

COPY requirements.txt .

RUN pip install pip --upgrade
RUN pip install --requirement requirements.txt --upgrade --user