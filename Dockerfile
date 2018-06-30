FROM ubuntu:16.04
MAINTAINER Frederic Fortier <fred@enigma.co>

FROM python:3

WORKDIR /usr/src/surface

COPY etc/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src .

CMD python -m surface