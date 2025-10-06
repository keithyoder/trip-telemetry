import adafruit_shtc3
from board import I2C
from devices.device import Device
from sensors.shtc3.temperature import Temperature
from sensors.shtc3.humidity import Humidity
from sensors.shtc3.dew_point import DewPoint

class SHTC3(Device):
    def __init__(self):
        super().__init__("SHTC3")
        self.device = adafruit_shtc3.SHTC3(I2C())
        self.values = {}
        self.sensors = [
            Temperature(self.device),
            Humidity(self.device),
            DewPoint(self.device)
        ]

    def is_connected(self):
        return self.device is not None