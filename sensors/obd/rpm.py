from sensors.sensor import Sensor
from dash_daq import LEDDisplay
from obd import commands


class RPM(Sensor):
    def __init__(self, device):
        super().__init__(device, "obd_rpm", "rpm", precision=0)
        self.cmd = commands.RPM
        self.max = 7000

    def value(self):
        try:
            return super().value(self.device.query(self.cmd))
        except:
            return None

    def dashboard_gauge(self):
        return LEDDisplay(
            id=self.key,
            label="RPM",
            value=0
        )