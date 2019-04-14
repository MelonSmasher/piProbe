# piProbe

Simple python script that sends temperature and humidity data gather on a RaspberryPi with a DHT22 sensor to InfluxDB.

## Setup

```bash
cd /opt;
git clone https://github.com/MelonSmasher/piProbe.git;
pip install -r requirements.txt;
cp config.example.json config.json;
mkdir /etc/piProbe;
ln -s /opt/piProbe/config.json /etc/piProbe/config.json;
# edit the config
vi /etc/piProbe/config.json;
python piProbe.py;
```