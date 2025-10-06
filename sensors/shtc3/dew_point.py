from sensors.sensor import Sensor
from math import log
from dash import dcc

class DewPoint(Sensor):
    def __init__(self, device):
        super().__init__(device, "shtc3_dewpoint", "C", precision=1)
        self.description = "Dew Point"

    def value(self):
        try:
            temperature, humidity = self.device.measurements
            dew_point = 243.04*(log(humidity/100)+((17.625*temperature)/(243.04+temperature)))/(17.625-log(humidity/100)-((17.625*temperature)/(243.04+temperature)))
            return super().value(dew_point)
        except:
            return None

    def figure(self, current, daily_range):
        return super().current_max_min(current, daily_range)

    def dashboard_gauge(self):
        return dcc.Graph(
            id=self.key
        )
