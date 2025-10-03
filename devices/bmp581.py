import board
from adafruit_bmp5xx import BMP5XX_I2C
from devices.device import Device

class BMP581(Device):
    def __init__(self, sea_level_pressure_hpa=1013.25):
        super().__init__("BMP581")
        self.sensor = BMP5XX_I2C(board.I2C())
        self.sensor.sea_level_pressure = sea_level_pressure_hpa
        self.values = self.null_values()

    def read(self):
        if self.sensor.data_ready:
            self.values = {
                "bmp581_temperature_C": round(self.sensor.temperature, 2),
                "bmp581_pressure_hPa": round(self.sensor.pressure, 2),
                "bmp581_altitude_m": round(self.sensor.altitude, 0)
            }
        else:
            self.values = self.null_values()

    def null_values(self):
        return {
            "bmp581_temperature_C": None,
            "bmp581_pressure_hPa": None,
            "bmp581_altitude_m": None
        }

    def is_connected(self):
        return self.sensor.data_ready