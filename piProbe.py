import time
import sys
import os
import datetime
import socket
import json
import Adafruit_DHT
from influxdb import InfluxDBClient

# Read our config
if os.path.isfile('/etc/piProbe/config.json'):
    with open('/etc/piProbe/config.json') as json_file:
        config = json.load(json_file)
elif os.path.isfile('./config.json'):
    with open('./config.json') as json_file:
        config = json.load(json_file)
else:
    print("Could not find configuration file.")
    exit(1)

# Store config in local vars
host = config['influxdb']['host']
port = config['influxdb']['port']
user = config['influxdb']['user']
password = config['influxdb']['password']
dbname = config['influxdb']['dbname']
interval = config['influxdb']['interval']
location = config['influxdb']['location']
ssl = config['influxdb']['ssl']
ssl_verify = config['influxdb']['ssl_verify']

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

# set the pinout
gpio_pin = config['gpio']['pin']
fahrenheit = config['gpio']['fahrenheit']

# Make a new influx client
client = InfluxDBClient(
    host=host,
    port=port,
    username=user,
    password=password,
    database=dbname,
    ssl=ssl,
    verify_ssl=ssl_verify
)
hostname = socket.gethostname()

try:
    while True:
        humidity, temperature = Adafruit_DHT.read_retry(sensor, gpio_pin)
        if humidity is not None and temperature is not None:

            iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.localtime())

            data = [
                {
                    "measurement": "temperature",
                    "tags": {
                        "host": hostname,
                        "location": location,
                    },
                    "time": iso,
                    "fields": {
                        "value_c": temperature,
                        "value_f": temperature * 9/5.0 + 32
                    }
                },
                {
                    "measurement": "humidity",
                    "tags": {
                        "host": hostname,
                        "location": location,
                    },
                    "time": iso,
                    "fields": {
                        "value": humidity
                    }
                }
            ]
            if client.write_points(data, time_precision='s'):
                print("yup")
            else:
                print("nope")
            time.sleep(interval)

except KeyboardInterrupt:
    pass
