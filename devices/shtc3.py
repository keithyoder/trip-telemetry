import adafruit_shtc3
from board import I2C
from devices.device import Device

class SHTC3(Device):
    def __init__(self):
        super().__init__("SHTC3")
        self.device = adafruit_shtc3.SHTC3(I2C())
        self.values = {}
        self.sensors = [
        ]

    def is_connected(self):
        return self.device is not None