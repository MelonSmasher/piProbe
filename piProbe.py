import sys
import os
import socket
import json
import time
import subprocess
from influxdb import InfluxDBClient
import Adafruit_DHT
from __future__ import print_function


def getConfig():
    # Pull the configuratin from env vars or the config file

    if os.environ.get('AM_I_IN_A_DOCKER_CONTAINER', False):
        c = {
            "debug": os.environ.get('DEBUG', False),
            "influxdb": {
                "host": os.environ.get('INFLUXDB_HOST', None),
                "port": int(os.environ.get('INFLUXDB_PORT', 8086)),
                "user": os.environ.get('INFLUXDB_USER', ""),
                "password": os.environ.get('INFLUXDB_PASSWORD', ""),
                "dbname": os.environ.get('INFLUXDB_DB', None),
                "interval": int(os.environ.get('INFLUXDB_INTERVAL', 10)),
                "ssl": os.environ.get('INFLUXDB_SSL', False),
                "ssl_verify": os.environ.get('INFLUXDB_SSL_VERIFY', False),
                "location_tag": os.environ.get('INFLUXDB_LOCATION_TAG', None)
            },
            "gpio": {
                "pin": int(os.environ.get('GPIO_PIN', 4)),
                "sensor": str(os.environ.get('GPIO_SENSOR', "")).upper()
            }
        }
    elif os.path.isfile('/etc/piProbe/config.json'):
        with open('/etc/piProbe/config.json') as json_file:
            c = json.load(json_file)
    elif os.path.isfile('./config.json'):
        with open('./config.json') as json_file:
            c = json.load(json_file)
    else:
        print("Could not find configuration file.")
        exit(1)

    if c['influxdb']['host'] is None:
        print("Please supply an INFLUXDB HOST value.")
        exit(1)

    if c['influxdb']['dbname'] is None:
        print("Please supply an INFLUXDB DB value.")
        exit(1)

    if c['influxdb']['location_tag'] is None:
        print("Please supply an INFLUXDB LOCATION TAG value.")
        exit(1)

    # set the adafruit sensor
    if c['gpio']['sensor'] == 'DHT22':
        c['gpio']['sensor'] = Adafruit_DHT.DHT22
    elif c['gpio']['sensor'] == 'DHT11':
        c['gpio']['sensor'] = Adafruit_DHT.DHT11
    elif c['gpio']['sensor'] == 'AM2302':
        c['gpio']['sensor'] = Adafruit_DHT.AM2302
    else:
        print("Please supply a valid GPIO SENSOR value (DHT11/DHT22/AM2302).")
        exit(1)

    # set the devicename for tags influx
    c['devicename'] = os.environ.get(
        'BALENA_DEVICE_NAME_AT_INIT', socket.gethostname())

    return c


def debugOut(valueC, valueF, valueH):
    print('Debug Values:')
    print('C: '+str(valueC))
    print('F: '+str(valueF))
    print('H: '+str(valueH)+'%')
    print('')


def mainLoop(config, client):
    # The main program loop
    # Poll the probe
    humidity, temperature = Adafruit_DHT.read_retry(
        config['gpio']['sensor'], int(config['gpio']['pin']))

    # Don't accept null values, if they're null we don't sleep and we poll the probe again
    if humidity is not None and temperature is not None:

        # Store our values
        valueC = float(temperature)
        valueF = float(temperature * 9/5.0 + 32)
        valueH = float(humidity)

        # If debug is enabled output the values to stdout
        if config['debug']:
            debugOut(valueC, valueF, valueH)

        # Filter stupid humidity readings, if the reading is high don't sleep and poll the probe again
        if humidity <= 100:

            # Format the measurements for influx
            data = [
                {
                    "measurement": "temperature",
                    "tags": {
                        "host": config['devicename'],
                        "location": config['influxdb']['location_tag'],
                    },
                    "fields": {
                        "value_c": valueC,
                        "value_f": valueF
                    }
                },
                {
                    "measurement": "humidity",
                    "tags": {
                        "host": config['devicename'],
                        "location": config['influxdb']['location_tag'],
                    },
                    "fields": {
                        "value": valueH
                    }
                }
            ]
            # Write the data to influx
            client.write_points(data, time_precision='s')
            # wait it out
            time.sleep(int(config['influxdb']['interval']))
    else:
        if config['debug']:
            print('No values found for either temp, humidity, or both. Trying again...')


# Run it!
try:
    # get the config
    config = getConfig()
    # Make a new influx client
    client = InfluxDBClient(
        host=config['influxdb']['host'],
        port=int(config['influxdb']['port']),
        username=config['influxdb']['user'],
        password=config['influxdb']['password'],
        database=config['influxdb']['dbname'],
        ssl=bool(config['influxdb']['ssl']),
        verify_ssl=bool(config['influxdb']['ssl_verify'])
    )
    while True:
        # Run the main loop
        mainLoop(config, client)
except KeyboardInterrupt:
    pass
