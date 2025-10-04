from sensors.sensor import Sensor
from dash_daq import Thermometer

class Temperature(Sensor):
    def __init__(self, device):
        super().__init__(device, "bmp581_temperature", "C")

    def value(self):
        try:
            return super().value(self.device.temperature)
        except:
            return None

    def dashboard_gauge(self):
        return Thermometer(
            id=self.key,
            min=0,
            max=40,
            value=20,
            height=120,
            showCurrentValue=True,
            units="C"
        )
