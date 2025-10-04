from sensors.sensor import Sensor
from dash_daq import LEDDisplay

class Pressure(Sensor):
    def __init__(self, device):
        super().__init__(device, "bmp581_pressure", "hPa", precision=1)

    def value(self):
        try:
            return super().value(self.device.pressure)
        except:
            return None

    def dashboard_gauge(self):
        return LEDDisplay(
            id=self.key,
            label="Pressure (hPa)",
            value=26.5
        )