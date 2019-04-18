FROM balenalib/raspberrypi3-python:3-build

WORKDIR /usr/src/app

COPY piProbe.py piProbe.py

COPY requirements.txt requirements.txt

RUN apt-get update \
  && apt-get upgrade --yes \
  && apt-get install build-essential python-dev python-openssl python-pip -y \
  && pip3 install --no-cache-dir --trusted-host pypi.python.org -r requirements.txt

ENV AM_I_IN_A_DOCKER_CONTAINER Yes

CMD modprobe w1-gpio && modprobe w1-therm modprobe i2c-dev && python3 piProbe.py