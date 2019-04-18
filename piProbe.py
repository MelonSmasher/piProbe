import sys
import os
import socket
import json
import time
import Adafruit_DHT
from influxdb import InfluxDBClient

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

try:
    while True:
        # Set our vars on each iteration to load changes on the fly
        hostname = socket.gethostname()
        # get the config
        config = getConfig()
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
        # set the pinout
        gpio_pin = config['gpio']['pin']
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
            host=host,
            port=port,
            username=user,
            password=password,
            database=dbname,
            ssl=ssl,
            verify_ssl=ssl_verify
        )

    humidity, temperature = Adafruit_DHT.read_retry(sensor, gpio_pin)
    # Don't accept null values, if they're null we don't sleep and we poll the probe again
    if humidity is not None and temperature is not None:
        # Filter stupid humidity readings, if the reading is high don't sleep and poll the probe again
        if humidity <= 100:
            # Format the measurements for influx
            data = [
                {
                    "measurement": "temperature",
                    "tags": {
                        "host": hostname,
                        "location": location,
                    },
                    "fields": {
                        "value_c": float(temperature),
                        "value_f": float(temperature * 9/5.0 + 32)
                    }
                },
                {
                    "measurement": "humidity",
                    "tags": {
                        "host": hostname,
                        "location": location,
                    },
                    "fields": {
                        "value": float(humidity)
                    }
                }
            ]
            # Write the data to influx
            client.write_points(data, time_precision='s')
            # Destroy the client
            client.close()
            # wait it out
            time.sleep(interval)

except KeyboardInterrupt:
    pass
