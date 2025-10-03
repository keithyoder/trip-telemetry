from sensors.sensor import Sensor
from dash_daq import LEDDisplay

class AmbientLight(Sensor):
    def __init__(self, device):
        super().__init__(device, "ltr390_ambient_light", "raw")

    def value(self):
        try:
            return super().value(self.device.light)
        except:
            return None

    def dashboard_gauge(self):
        return LEDDisplay(
            id=self.key,
            label="Ambient Light (lux)",
            value=26.5
        )