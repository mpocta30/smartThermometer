# Smart Thermometer
This project allows the user to attach a DS18B20 sesnor to a raspberry pi and see the current and historical temperature in both Fahrenheit and Celsius.

## Enable 1-Wire Interface
1. In the terminal type: `sudo raspi-config`
2. Select **Interfacing Options**
3. Select **1-Wire**
4. Click **Yes**
5. Click **Ok**
6. If you would like to enable SSH and/or VNC click **No** and continue to step 7, otherwise, click **Yes** and allow your RaspberryPi to reboot

### Enable SSH and/or VNC
7. Click **SSH** or **VNC** and repeat steps 4 and 5.  Optionally repeat the steps but click **VNC**

## Installing mongodb on to RaspberryPi
Type the following commands in to the terminal on your RaspberryPi:
1. `apt-get update`
2. `apt-get upgrade`
3. `apt-get dist-upgrade`
4. `reboot`
5. `apt-get install mongodb`

## Installing the application
Type the following commands in to the terminal on your RaspberryPi:
1. `git clone https://github.com/mpocta30/smartThermometer.git`
2. `cd smartThermometer`
3. `pip install -r requirements.txt`

## Set Environment Variables
Type the following commands in to the terminal on your RaspberryPi:
1. `export TWILIO_ACCOUNT_SID="Your Twilio SID"`
2. `export TWILIO_AUTH_TOKEN="Your Twilio Token"`

## Enjoy!
