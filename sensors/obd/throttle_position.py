from sensors.sensor import Sensor
from dash_daq import LEDDisplay
from obd import commands


class ThrottlePosition(Sensor):
    def __init__(self, device):
        super().__init__(device, "obd_throttle_position", "%", precision=1)
        self.cmd = commands.THROTTLE_POS
        self.min = 0
        self.max = 100

    def value(self):
        try:
            return super().value(self.device.query(self.cmd))
        except:
            return None

    def dashboard_gauge(self):
        return LEDDisplay(
            id=self.key,
            label="Throttle Position (%)",
            value=0
        )