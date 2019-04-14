import time
import sys
import os
import datetime
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
measurement = config['influxdb']['measurement']
location = config['influxdb']['location']

# set the adafruit sensor
if config['gpio']['sensor'] == 'DHT22':
    sensor = Adafruit_DHT.DHT22
elif config['gpio']['sensor'] == 'DHT11':
    sensor = Adafruit_DHT.DHT11
else:
    print("The sensor entered is not supported.")
    exit(2)

# set the pinout
gpio_pin = config['gpio']['pin']

# Make a new influx client
client = InfluxDBClient(host, port, user, password, dbname)

try:
    while True:
        humidity, temperature = Adafruit_DHT.read_retry(sensor, gpio_pin)
        iso = time.ctime()
        data = [
            {
                "measurement": measurement,
                "tags": {
                    "location": location,
                },
                "time": iso,
                "fields": {
                    "temperature": temperature,
                    "humidity": humidity
                }
            }
        ]
        client.write_points(data)
        time.sleep(interval)

except KeyboardInterrupt:
    pass
