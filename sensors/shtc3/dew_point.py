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
            kelvin = 243.04 + temperature
            log_humidity = log(humidity / 100)
            dew_point = 243.04*(log_humidity+((17.625*temperature)/kelvin)) / (17.625-log_humidity-((17.625*temperature)/kelvin))
            return super().value(dew_point)
        except:
            return None

    def figure(self, current, daily_range):
        return super().current_max_min(current, daily_range)

    def dashboard_gauge(self):
        return dcc.Graph(
            id=self.key
        )
