import board
from adafruit_bmp5xx import BMP5XX
from sensors.sensor import Sensor

class BMP581(Sensor):
    def __init__(self):
        super().__init__("BMP581")
        self.sensor = BMP5XX()
        self.sensor.begin()

    def read(self):
        try:
            data = self.sensor.get_sensor_data()
            self.values = {
                "temperature_C": data.temperature_C,
                "pressure_hPa": data.pressure_hPa,
                "altitude_m": data.altitude_m
            }
        except:
            self.values = {
                "temperature_C": None,
                "pressure_hPa": None,
                "altitude_m": None
            }

    def is_connected(self):
        return self.sensor.is_connected()