FROM balenalib/raspberrypi3-python

COPY piProbe.py piProbe.py

COPY requirements.txt requirements.txt

RUN pip install --trusted-host pypi.python.org -r requirements.txt

ENV AM_I_IN_A_DOCKER_CONTAINER Yes

CMD modprobe w1-gpio && modprobe w1-therm modprobe i2c-dev && python