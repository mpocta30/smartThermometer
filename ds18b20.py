from w1thermsensor import w1thermsensor
import random


class thermSensor:
    def __init__(self):
        #self.sensor = w1thermsensor()
        self.sensor = 'Hello'

    def getTemp(self):
        #cTemp = self.sensor.get_temperature()
        cTemp = random.randint(0, 100)
        fTemp = round((cTemp*1.8) + 32, 2)

        return cTemp, fTemp