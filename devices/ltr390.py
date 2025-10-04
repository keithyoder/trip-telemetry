import adafruit_ltr390
from board import I2C
from devices.device import Device
from sensors.ltr390.ambient_light import AmbientLight
from sensors.ltr390.lux import Lux
from sensors.ltr390.uv_index import UVIndex

class LTR390(Device):
    def __init__(self):
        super().__init__("LTR390")
        self.device = adafruit_ltr390.LTR390(I2C())
        self.device.gain = adafruit_ltr390.GAIN_1X
        self.device.resolution = adafruit_ltr390.RESOLUTION_20BIT
        self.device.mode = adafruit_ltr390.MODE_UV_AND_ALS
        self.values = {}
        self.sensors = [
            AmbientLight(self.device),
            Lux(self.device),
            UVIndex(self.device)
        ]

    def is_connected(self):
        return self.device is not None