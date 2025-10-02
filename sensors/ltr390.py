import board
import adafruit_ltr390
from sensors.sensor import Sensor

class LTR390(Sensor):
    def __init__(self):
        super().__init__("LTR390")
        self.sensor = adafruit_ltr390.LTR390(board.I2C())
        self.values = self.null_values()

    def read(self):
        self.values = {
            "ltr390_ambient_light": self.sensor.ambient_light,
            "ltr390_lux": self.sensor.lux,
            "ltr390_uv_index": self.sensor.uv_index
        }

    def null_values(self):
        return {
            "ltr390_ambient_light": None,
            "ltr390_lux": None,
            "ltr390_uv_index": None
        }

    def is_connected(self):
        return self.sensor.is_connected()