from devices.device import Device
from sensors.ltr390.ambient_light import AmbientLight
from sensors.ltr390.lux import Lux
from sensors.ltr390.uv_index import UVIndex

class LTR390(Device):
    def __init__(self):
        super().__init__("LTR390")
        try:
            import adafruit_ltr390
            from board import I2C
            self.device = adafruit_ltr390.LTR390(I2C())
            self.device.gain = adafruit_ltr390.Gain.GAIN_1X
            self.device.resolution = adafruit_ltr390.Resolution.RESOLUTION_20BIT
        except:
            self.device = None
        self.values = {}
        self.sensors = [
            AmbientLight(self.device),
            Lux(self.device),
            UVIndex(self.device)
        ]

    def is_connected(self):
        return self.device is not None