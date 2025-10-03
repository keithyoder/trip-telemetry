from sensors.sensor import Sensor
from dash_daq import LEDDisplay

class UVIndex(Sensor):
    def __init__(self, device):
        super().__init__(device, "ltr390_uv_index", "raw")

    def value(self):
        try:
            return super().value(self.device.uvi)
        except:
            return None
        
    def dashboard_gauge(self):
        return LEDDisplay(
            id=self.key,
            label="UV Index",
            value=26.5
        )