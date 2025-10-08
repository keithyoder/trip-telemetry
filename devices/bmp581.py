from devices.device import Device
from sensors.bmp581.temperature import Temperature
from sensors.bmp581.pressure import Pressure

class BMP581(Device):
    def __init__(self, sea_level_pressure_hpa=1013.25):
        super().__init__("BMP581")
        try:
            import board
            from adafruit_bmp5xx import BMP5XX_I2C
            from board import I2C
            self.device = BMP5XX_I2C(board.I2C())
            self.device.sea_level_pressure = sea_level_pressure_hpa
        except:
            self.device = None
        self.sensors = [
            Temperature(self.device),
            Pressure(self.device)
        ]
        self.values = {}

    def is_connected(self):
        return False if self.device is None else self.device.data_ready