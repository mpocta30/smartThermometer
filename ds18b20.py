from w1thermsensor import W1ThermSensor
import random


class thermSensor:
    def __init__(self):
        self.sensor = W1ThermSensor()

    def getTemp(self):
        cTemp = self.sensor.get_temperature()
        fTemp = round((cTemp*1.8) + 32, 2)

        return cTemp, fTemp
