from sensors.sensor import Sensor
from dash_daq import LEDDisplay

class Temperature(Sensor):
    def __init__(self, device):
        super().__init__(device, "bmp581_temperature", "C")

    def value(self):
        try:
            return super().value(self.device.temperature)
        except:
            return None

    def dashboard_gauge(self):
        return LEDDisplay(
            id=self.key,
            label="Temperature (C)",
            value=26.5
        )