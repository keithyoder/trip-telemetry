from sensors.sensor import Sensor
from dash_daq import LEDDisplay

class Humidity(Sensor):
    def __init__(self, device):
        super().__init__(device, "shtc3_humidity", "C", precision=1)

    def value(self):
        try:
            _, humidity = self.device.measurements
            return super().value(humidity)
        except:
            return None

    def dashboard_gauge(self):
        return LEDDisplay(
            id=self.key,
            label="Relative Humidity (%)",
            value=26.5
        )