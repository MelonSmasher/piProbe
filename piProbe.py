import sys
import os
import socket
import json
import time
import subprocess
from influxdb import InfluxDBClient
import Adafruit_DHT

# Pull the configuratin from env vars or the config file


def getConfig():
    if os.environ.get('AM_I_IN_A_DOCKER_CONTAINER', False):
        return {
            "influxdb": {
                "host": os.environ.get('INFLUXDB_HOST', "127.0.0.1"),
                "port": int(os.environ.get('INFLUXDB_PORT', 8086)),
                "user": os.environ.get('INFLUXDB_USER', ""),
                "password": os.environ.get('INFLUXDB_PASSWORD', ""),
                "dbname": os.environ.get('INFLUXDB_DB', "pi-probes"),
                "interval": int(os.environ.get('INFLUXDB_INTERVAL', 10)),
                "ssl": os.environ.get('INFLUXDB_SSL', False),
                "ssl_verify": os.environ.get('INFLUXDB_SSL_VERIFY', False),
                "location_tag": os.environ.get('INFLUXDB_LOCATION_TAG', "Winterfell")
            },
            "gpio": {
                "pin": int(os.environ.get('GPIO_PIN', 4)),
                "sensor": os.environ.get('GPIO_SENSOR', "AM2302")
            }
        }
    elif os.path.isfile('/etc/piProbe/config.json'):
        with open('/etc/piProbe/config.json') as json_file:
            return json.load(json_file)
    elif os.path.isfile('./config.json'):
        with open('./config.json') as json_file:
            return json.load(json_file)
    else:
        print("Could not find configuration file.")
        exit(1)

# The main program loop


def mainLoop():
    # device name
    hostName = os.environ.get(
        'BALENA_DEVICE_NAME_AT_INIT', socket.gethostname())
    # get the config
    config = getConfig()
    # set the adafruit sensor
    if config['gpio']['sensor'].upper() == 'DHT22':
        sensor = Adafruit_DHT.DHT22
    elif config['gpio']['sensor'].upper() == 'DHT11':
        sensor = Adafruit_DHT.DHT11
    elif config['gpio']['sensor'].upper() == 'AM2302':
        sensor = Adafruit_DHT.AM2302
    else:
        print("The sensor entered is not supported.")
        exit(2)
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
    # Poll the probe
    humidity, temperature = Adafruit_DHT.read_retry(
        sensor, int(config['gpio']['pin']))
    # Don't accept null values, if they're null we don't sleep and we poll the probe again
    if humidity is not None and temperature is not None:
        # Filter stupid humidity readings, if the reading is high don't sleep and poll the probe again
        if humidity <= 100:
            # Format the measurements for influx
            data = [
                {
                    "measurement": "temperature",
                    "tags": {
                        "host": hostName,
                        "location": config['influxdb']['location_tag'],
                    },
                    "fields": {
                        "value_c": float(temperature),
                        "value_f": float(temperature * 9/5.0 + 32)
                    }
                },
                {
                    "measurement": "humidity",
                    "tags": {
                        "host": hostName,
                        "location": config['influxdb']['location_tag'],
                    },
                    "fields": {
                        "value": float(humidity)
                    }
                }
            ]
            # Write the data to influx
            client.write_points(data, time_precision='s')
            # wait it out
            time.sleep(int(config['influxdb']['interval']))
            # Destory the client
            client.close()
            client = None


# Run it!
try:
    while True:
        # Run the main loop
        mainLoop()
except KeyboardInterrupt:
    pass
