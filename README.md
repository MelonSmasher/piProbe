# piProbe

Simple python script that sends temperature and humidity data gathered on a RaspberryPi with a DHT11/DHT22/AM2302 sensor to InfluxDB.

## Setup

```bash
cd /opt;
git clone https://github.com/MelonSmasher/piProbe.git;
cd piProbe/;
pip install -r requirements.txt;
cp config.example.json config.json;
mkdir /etc/piProbe;
ln -s /opt/piProbe/config.json /etc/piProbe/config.json;
# edit the config
vi /etc/piProbe/config.json;
python piProbe.py;
```