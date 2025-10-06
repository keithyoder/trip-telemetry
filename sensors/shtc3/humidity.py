from sensors.sensor import Sensor
from dash import dcc

class Humidity(Sensor):
    def __init__(self, device):
        super().__init__(device, "shtc3_humidity", "C", precision=1)

    def value(self):
        try:
            _, humidity = self.device.measurements
            return super().value(humidity)
        except:
            return None

    def figure(self, min, max, current):
        return super().current_max_min(max, min, current)

    def dashboard_gauge(self):
        return dcc.Graph(
            id=self.key
        )
