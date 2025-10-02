import board
from adafruit_bmp5xx import BMP5XX_I2C
from sensors.sensor import Sensor

class BMP581(Sensor):
    def __init__(self, sea_level_pressure_hpa=1013.25):
        super().__init__("BMP581")
        self.sensor = BMP5XX_I2C(board.I2C())
        self.sensor.sea_level_pressure = sea_level_pressure_hpa

    def read(self):
        if self.sensor.data_ready:
            self.values = {
                "temperature_C": self.sensor.temperature,
                "pressure_hPa": self.sensor.pressure,
                "altitude_m": self.sensor.altitude
            }
        else:
            self.values = {
                "temperature_C": None,
                "pressure_hPa": None,
                "altitude_m": None
            }

    def is_connected(self):
        return self.sensor.is_connected()