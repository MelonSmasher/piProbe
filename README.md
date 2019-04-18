# piProbe

Simple python script that sends temperature and humidity data gathered on a RaspberryPi with a DHT11/DHT22/AM2302 sensor to InfluxDB.

## Setup

```bash
cd /opt;
git clone https://github.com/MelonSmasher/piProbe.git;
cd piProbe/;
# The first run of pip will fail, run it twice.
pip install -r requirements.txt;
pip install -r requirements.txt;
cp config.example.json config.json;
mkdir /etc/piProbe;
ln -s /opt/piProbe/config.json /etc/piProbe/config.json;
# edit the config
vi /etc/piProbe/config.json;
python piProbe.py;
```

## Service Setup

```bash
sudo cp /opt/piProbe/piProbe.service /etc/systemd/system/piProbe.service;
# Change the user from root if needed * probably a good idea for security reasons.
sudo vi /etc/systemd/system/piProbe.service;
sudo systemctl daemon-reload;
systemctl enable piProbe.service;
service piProbe start;
```

## Grafana

I've supplied an example Grafana dashboard in the Grafana folder. You can import the JSON file.

![Screen Shot Grafana](/screen/screen-1.png)

## Balena Setup

* Create a new Balena application.
  * Select Raspberry Pi 3 as the device type for the application.
    * Create an image to flash on the SD card from within that application.
* Flash the image to your SD card with balenaEtcher.
  * Re-insert the SD card after the image has been flashed and open `config.txt` (located on resin-boot) with a text editor.
    * Add the following line to the file `dtoverlay=w1-gpio`
      * Then save the file and eject the card.
* Power on the pi with your SD card in the Pi.
* Clone this repo to your workstation.
* From within the local repo directory run: `balena push <app-name>` the app name is the name of the application from the first step.
* Profit
