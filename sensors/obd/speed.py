from sensors.sensor import Sensor
from dash_daq import LEDDisplay
from obd import commands

class Speed(Sensor):
    def __init__(self, device):
        super().__init__(device, "obd_speed", "kph", precision=2)
        self.cmd = commands.SPEED 

    def value(self):
        try:
            return super().value(self.device.query(self.cmd))
        except:
            return None

    def dashboard_gauge(self):
        return LEDDisplay(
            id=self.key,
            label="Speed (kph)",
            value=26.5
        )